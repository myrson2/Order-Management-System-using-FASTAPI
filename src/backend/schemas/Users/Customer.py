from typing import Literal
from backend.schemas.Users.User import UserCreate, EnumType
from pydantic import Field

class Customer(UserCreate):
    user_type: Literal[EnumType.CUSTOMER] = EnumType.CUSTOMER
    rewards: float = Field(default=0)