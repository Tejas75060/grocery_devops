"""Pydantic request/response schemas."""
import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, Field


class ProductOut(BaseModel):
    sku: str
    name: str
    price: float
    stock: int

    class Config:
        from_attributes = True


class OrderItemIn(BaseModel):
    sku: str
    quantity: int = Field(gt=0)


class OrderItemOut(BaseModel):
    sku: str
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    items: List[OrderItemIn] = Field(min_length=1)


class DeliveryOut(BaseModel):
    agent_name: str
    status: str
    assigned_at: dt.datetime

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    customer_name: str
    address: str
    status: str
    total: float
    created_at: dt.datetime
    items: List[OrderItemOut] = []
    delivery: Optional[DeliveryOut] = None

    class Config:
        from_attributes = True


class DeliveryAssign(BaseModel):
    agent_name: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str
