import random
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, ValidationError
from uuid import uuid4, UUID

class Customer(BaseModel):
    # model_config = ConfigDict(strict = True)
    id: UUID = Field(default_factory=uuid4)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: EmailStr
    phone: str = Field(max_length=11)
    password: str = Field(min_length=8)

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        if value.endswith('@gmail.com'):
            return value
        else:
            raise ValidationError('Email address is not valid')

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value):
        if value.startswith('09') or len(value) == 11:
            return value
        else:
            raise ValidationError('Password is not valid')

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain an uppercase letter")

        if not any(char.islower() for char in value):
            raise ValueError("Password must contain a lowercase letter")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain a number")

        if not any(not char.isalnum() for char in value):
            raise ValueError("Password must contain a special character")

        return value

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_dict(cls, data: dict) -> Customer:
        return cls(**data)  
    
    def to_dict(self):
        return self.model_dump(mode='json')