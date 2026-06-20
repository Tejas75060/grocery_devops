"""Seed the catalogue with sample grocery products (idempotent)."""
import logging

from app.database import Base, SessionLocal, engine
from app import models

logger = logging.getLogger("grocery.seed")

SAMPLE_PRODUCTS = [
    {"sku": "MILK-1L", "name": "Milk 1L", "price": 1.20, "stock": 200},
    {"sku": "BREAD-WHT", "name": "White Bread", "price": 0.95, "stock": 150},
    {"sku": "EGGS-12", "name": "Eggs (dozen)", "price": 2.50, "stock": 120},
    {"sku": "RICE-5KG", "name": "Rice 5kg", "price": 6.80, "stock": 80},
    {"sku": "BANANA-1KG", "name": "Bananas 1kg", "price": 1.10, "stock": 90},
    {"sku": "TOMATO-1KG", "name": "Tomatoes 1kg", "price": 1.60, "stock": 70},
    {"sku": "COFFEE-250G", "name": "Coffee 250g", "price": 4.20, "stock": 60},
    {"sku": "OIL-1L", "name": "Cooking Oil 1L", "price": 3.30, "stock": 100},
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        created = 0
        for p in SAMPLE_PRODUCTS:
            exists = (
                db.query(models.Product)
                .filter(models.Product.sku == p["sku"])
                .first()
            )
            if not exists:
                db.add(models.Product(**p))
                created += 1
        db.commit()
        logger.info("Seed complete; %s new products added", created)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed()
