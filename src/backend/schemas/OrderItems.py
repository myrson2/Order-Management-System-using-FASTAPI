from uuid import uuid4, UUID
from pydantic import BaseModel, Field, field_validator


class OrderItem(BaseModel):
    order_item_id: str
    total_price: float
    product_id: str
    quantity: float = Field(gt=0)
    product_name: str
    unit_price: float


class OrderItemCreate(OrderItem):
    pass
