"""SQLAlchemy ORM models for the grocery domain."""
import datetime as dt

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=0)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    # Order lifecycle: PLACED -> CONFIRMED -> ASSIGNED -> OUT_FOR_DELIVERY -> DELIVERED
    status = Column(String, nullable=False, default="PLACED", index=True)
    total = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(
        DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow
    )

    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    delivery = relationship(
        "Delivery",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    sku = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0.0)

    order = relationship("Order", back_populates="items")


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    agent_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ASSIGNED")
    assigned_at = Column(DateTime, default=dt.datetime.utcnow)

    order = relationship("Order", back_populates="delivery")
