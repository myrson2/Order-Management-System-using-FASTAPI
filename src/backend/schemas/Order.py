from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from datetime import datetime
from backend.schemas.OrderItems import OrderItem


class Order(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    customer_id: UUID
    order_date: datetime = Field(default_factory=datetime.now)
    order_list: list[OrderItem] = Field(default_factory=list)
    total_amount: float
    


    