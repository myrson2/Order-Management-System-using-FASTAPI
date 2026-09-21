from uuid import uuid4, UUID
from pydantic import BaseModel, Field, field_validator


class OrderItem(BaseModel):
    order_item_id: UUID = Field(default_factory=uuid4)
    total_price: float

class OrderItemCreate(OrderItem):
    product_id: str
    quantity: float = Field(gt=0)
