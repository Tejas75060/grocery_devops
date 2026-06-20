"""FastAPI application entrypoint for the Grocery Delivery Platform."""
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import get_settings
from app.database import Base, engine, get_db
from app.logging_config import configure_logging
from app.metrics import (
    ACTIVE_ORDERS,
    MetricsMiddleware,
    ORDERS_DELIVERED,
    ORDERS_PLACED,
)
from app.seed import seed

configure_logging()
logger = logging.getLogger("grocery.api")
settings = get_settings()

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(MetricsMiddleware)

STATIC_DIR = Path(__file__).parent / "static"


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    seed()
    logger.info("Application started in %s environment", settings.environment)


# ----------------------------- Health & metrics -----------------------------
@app.get("/health", tags=["ops"])
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.get("/ready", tags=["ops"])
def ready(db: Session = Depends(get_db)) -> dict:
    db.execute(models.Product.__table__.select().limit(1))
    return {"status": "ready"}


@app.get("/metrics", tags=["ops"])
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ------------------------------- Inventory ----------------------------------
@app.get("/api/inventory", response_model=List[schemas.ProductOut], tags=["inventory"])
def inventory(db: Session = Depends(get_db)):
    """Inventory check — list all products and current stock."""
    return crud.list_products(db)


@app.get(
    "/api/inventory/{sku}", response_model=schemas.ProductOut, tags=["inventory"]
)
def inventory_item(sku: str, db: Session = Depends(get_db)):
    product = crud.get_product(db, sku)
    if product is None:
        raise HTTPException(status_code=404, detail="SKU not found")
    return product


# --------------------------------- Orders -----------------------------------
@app.post("/api/orders", response_model=schemas.OrderOut, status_code=201, tags=["orders"])
def place_order(payload: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Place an order — validates stock and decrements inventory."""
    try:
        order = crud.create_order(db, payload)
    except crud.InventoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    ORDERS_PLACED.inc()
    _recount_active(db)
    logger.info("Order placed", extra={"order_id": order.id, "total": order.total})
    return order


@app.get("/api/orders", response_model=List[schemas.OrderOut], tags=["orders"])
def list_orders(db: Session = Depends(get_db)):
    return crud.list_orders(db)


@app.get("/api/orders/{order_id}", response_model=schemas.OrderOut, tags=["orders"])
def track_order(order_id: int, db: Session = Depends(get_db)):
    """Track order status."""
    order = crud.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post(
    "/api/orders/{order_id}/assign",
    response_model=schemas.OrderOut,
    tags=["delivery"],
)
def assign_delivery(
    order_id: int,
    payload: Optional[schemas.DeliveryAssign] = None,
    db: Session = Depends(get_db),
):
    """Delivery assignment — attach a delivery agent to a confirmed order."""
    agent = payload.agent_name if payload else None
    try:
        order = crud.assign_delivery(db, order_id, agent)
    except crud.InventoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    logger.info(
        "Delivery assigned",
        extra={"order_id": order.id, "agent": order.delivery.agent_name},
    )
    return order


@app.patch(
    "/api/orders/{order_id}/status",
    response_model=schemas.OrderOut,
    tags=["orders"],
)
def update_order_status(
    order_id: int, payload: schemas.StatusUpdate, db: Session = Depends(get_db)
):
    try:
        order = crud.update_status(db, order_id, payload.status)
    except crud.InventoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if order.status == "DELIVERED":
        ORDERS_DELIVERED.inc()
    _recount_active(db)
    return order


def _recount_active(db: Session) -> None:
    active = (
        db.query(models.Order)
        .filter(models.Order.status.notin_(["DELIVERED", "CANCELLED"]))
        .count()
    )
    ACTIVE_ORDERS.set(active)


# -------------------------------- Frontend ----------------------------------
@app.get("/", response_class=HTMLResponse, tags=["ui"])
def dashboard():
    index = STATIC_DIR / "index.html"
    return HTMLResponse(index.read_text())


# Serve static assets (CSS/JS) if any are added later.
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
