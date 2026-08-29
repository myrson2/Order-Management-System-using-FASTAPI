from uuid import uuid4, UUID
from pydantic import BaseModel, Field

class OrderItem(BaseModel):
    order_item_id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    product_id: str
    quantity: float = Field(gt=0)
    unit_price: float
    total_price: float