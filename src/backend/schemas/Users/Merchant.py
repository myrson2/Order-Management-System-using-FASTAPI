from typing import Literal
from pydantic import Field
from uuid import UUID
from backend.schemas.Users.User import UserCreate, EnumType

class Merchant(UserCreate):
    user_type: Literal[EnumType.MERCHANT] = EnumType.MERCHANT
    store_name: str = Field(..., min_length=1, max_length=50)
    tax_id: UUID = Field(...)

