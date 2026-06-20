"""Business logic / data-access layer."""
import random
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas

VALID_TRANSITIONS = {
    "PLACED": {"CONFIRMED", "CANCELLED"},
    "CONFIRMED": {"ASSIGNED", "CANCELLED"},
    "ASSIGNED": {"OUT_FOR_DELIVERY", "CANCELLED"},
    "OUT_FOR_DELIVERY": {"DELIVERED"},
    "DELIVERED": set(),
    "CANCELLED": set(),
}

DELIVERY_AGENTS = ["Asha", "Ravi", "Meera", "Karan", "Sana", "Vivek"]


class InventoryError(Exception):
    """Raised when an order cannot be fulfilled from current stock."""


def list_products(db: Session) -> List[models.Product]:
    return db.query(models.Product).order_by(models.Product.sku).all()


def get_product(db: Session, sku: str) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.sku == sku).first()


def create_order(db: Session, payload: schemas.OrderCreate) -> models.Order:
    """Validate stock, decrement inventory, and persist the order atomically."""
    total = 0.0
    resolved_items = []
    for item in payload.items:
        product = get_product(db, item.sku)
        if product is None:
            raise InventoryError(f"Unknown SKU: {item.sku}")
        if product.stock < item.quantity:
            raise InventoryError(
                f"Insufficient stock for {item.sku}: "
                f"requested {item.quantity}, available {product.stock}"
            )
        resolved_items.append((product, item.quantity))
        total += product.price * item.quantity

    order = models.Order(
        customer_name=payload.customer_name,
        address=payload.address,
        status="CONFIRMED",
        total=round(total, 2),
    )
    db.add(order)
    db.flush()  # assign order.id

    for product, qty in resolved_items:
        product.stock -= qty
        db.add(
            models.OrderItem(
                order_id=order.id,
                sku=product.sku,
                quantity=qty,
                unit_price=product.price,
            )
        )

    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def list_orders(db: Session, limit: int = 50) -> List[models.Order]:
    return (
        db.query(models.Order)
        .order_by(models.Order.created_at.desc())
        .limit(limit)
        .all()
    )


def assign_delivery(
    db: Session, order_id: int, agent_name: Optional[str] = None
) -> models.Order:
    order = get_order(db, order_id)
    if order is None:
        raise InventoryError("Order not found")
    if order.status not in {"CONFIRMED"}:
        raise InventoryError(
            f"Order {order_id} cannot be assigned from status {order.status}"
        )

    agent = agent_name or random.choice(DELIVERY_AGENTS)
    if order.delivery is None:
        order.delivery = models.Delivery(agent_name=agent, status="ASSIGNED")
    else:
        order.delivery.agent_name = agent
        order.delivery.status = "ASSIGNED"
    order.status = "ASSIGNED"
    db.commit()
    db.refresh(order)
    return order


def update_status(db: Session, order_id: int, new_status: str) -> models.Order:
    order = get_order(db, order_id)
    if order is None:
        raise InventoryError("Order not found")
    allowed = VALID_TRANSITIONS.get(order.status, set())
    if new_status not in allowed:
        raise InventoryError(
            f"Invalid transition {order.status} -> {new_status}"
        )
    order.status = new_status
    if order.delivery and new_status in {"OUT_FOR_DELIVERY", "DELIVERED"}:
        order.delivery.status = new_status
    db.commit()
    db.refresh(order)
    return order
