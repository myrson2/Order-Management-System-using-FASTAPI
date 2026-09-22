from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict

class Cart(BaseModel):
    id: UUID = Field(default_factory=uuid4)

class CartCreate(Cart):
    product_name: str = Field(...)
    customer_id: str = Field(...)
    merchant_id: str = Field(...)
    product_id: str = Field(...)
    quantity: int = Field(gt=0)

class CartResponse(BaseModel):
    id: UUID
    product_name: str = Field(...)
    customer_id: str = Field(...)
    merchant_id: str = Field(...)
    product_id: str = Field(...)

class CartUpdate(BaseModel):
    product_name: str = Field(...)
    quantity: int = Field(gt=0)
