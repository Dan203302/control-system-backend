from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from .models import OrderStatus


class OrderItem(BaseModel):
    sku: str = Field(min_length=1)
    qty: int = Field(ge=1)
    price: float = Field(ge=0)


class CreateOrderIn(BaseModel):
    items: List[OrderItem]


class UpdateStatusIn(BaseModel):
    status: OrderStatus


class OrderOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    items: list
    status: OrderStatus
    total_amount: float

    class Config:
        from_attributes = True


class OrdersPage(BaseModel):
    items: List[OrderOut]
    total: int
    page: int
    size: int
