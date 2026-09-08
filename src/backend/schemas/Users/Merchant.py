import uuid
from typing import Literal
from pydantic import Field, field_validator
from uuid import UUID, uuid4
from backend.schemas.Users.User import EnumType, UserCreate, UserResponse


class Merchant(UserCreate):
    user_type: Literal[EnumType.MERCHANT] = EnumType.MERCHANT
    store_name: str = Field(..., min_length=1, max_length=50)
    tax_id: UUID = Field(default_factory=uuid4)

class MerchantResponse(UserResponse):
    user_type: Literal[EnumType.MERCHANT] = EnumType.MERCHANT
    store_name: str = Field(..., min_length=1, max_length=50)
    tax_id: UUID = Field(default_factory=uuid4)

