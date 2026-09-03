from typing import Literal
from backend.schemas.Users.User import EnumType, User, UserCreate, UserResponse
from pydantic import Field, field_validator


class Customer(UserCreate):
    user_type: Literal[EnumType.CUSTOMER] = EnumType.CUSTOMER
    rewards: float = Field(default=0)

class CustomerResponse(UserResponse):
    user_type: Literal[EnumType.CUSTOMER] = EnumType.CUSTOMER
    rewards: float = Field(default=0)