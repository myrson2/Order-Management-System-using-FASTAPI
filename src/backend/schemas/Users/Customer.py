from typing import Literal
from backend.schemas.Users.User import EnumType, User, UserCreate
from pydantic import Field, field_validator


class Customer(UserCreate):
    user_type: Literal[EnumType.CUSTOMER] = EnumType.CUSTOMER
    rewards: float = Field(default=0)