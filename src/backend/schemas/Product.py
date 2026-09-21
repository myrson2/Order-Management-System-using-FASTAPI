import backend.utilities as utils
from pydantic import BaseModel, Field, field_validator
from uuid import UUID, uuid4

def generate_id() -> str:
    """
    Description / Purpose:
        Generates a formatted unique product identifier string with a 'PRD-' prefix.

    Args / Parameters:
        None.

    Returns:
        str: Formatted product ID string (e.g., 'PRD-3F2A19C8').

    Constraints / Notes:
        Delegates collision-safe hex string generation to backend.utilities.generate_product_id.
    """
    return f"PRD-{utils.generate_product_id()}"

class Product(BaseModel):
    id: str = Field(default_factory=generate_id)

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """
        Description / Purpose:
            Instantiates a Product model from a dictionary payload.

        Args / Parameters:
            data (dict): Dictionary containing product attributes.

        Returns:
            Product: Validated Product model instance.

        Constraints / Notes:
            Unpacks keys into model constructor; triggers all Pydantic field validators.
        """
        return cls(**data)

    def to_dict(self) -> dict:
        """
        Description / Purpose:
            Serializes the Product model into a JSON-compatible dictionary.

        Args / Parameters:
            None.

        Returns:
            dict: Dictionary with UUIDs and complex types serialized as JSON strings.

        Constraints / Notes:
            Uses mode='json' to ensure output is safe for JSON file persistence and HTTP transmission.
        """
        return self.model_dump(mode="json")

class ProductCreate(Product):
    merchant_id: UUID
    stock_quantity: int = Field(..., ge=0, strict=True)
    unit_price: float = Field(..., strict=True)
    product_name: str = Field(..., min_length=1, max_length=50, strict=True)

    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, value: str) -> str:
        """
        Description / Purpose:
            Validates that the product name is not empty or composed solely of whitespace,
            and strips leading/trailing spaces.

        Args / Parameters:
            value (str): The raw product name string.

        Returns:
            str: The sanitized, stripped product name string.

        Constraints / Notes:
            Raises ValueError if the stripped string is empty.
        """
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Product name cannot be empty or contain only whitespace.")
        return stripped_value

    @field_validator("unit_price")
    @classmethod
    def validate_unit_price(cls, value: float) -> float:
        """
        Description / Purpose:
            Validates that unit price is strictly positive (> 0) and has at most 2 decimal places.

        Args / Parameters:
            value (float): The unit price of the product.

        Returns:
            float: The validated unit price rounded to 2 decimal places.

        Constraints / Notes:
            Raises ValueError if unit price is less than or equal to 0, or exceeds 2 decimal places.
        """
        if value <= 0:
            raise ValueError("Unit price must be strictly greater than zero.")
        if round(value, 2) != value:
            raise ValueError("Unit price cannot have more than 2 decimal places.")
        return round(value, 2)

    @field_validator("stock_quantity")
    @classmethod
    def validate_stock_quantity(cls, value: int) -> int:
        """
        Description / Purpose:
            Validates that stock quantity is non-negative and does not exceed maximum inventory limits.

        Args / Parameters:
            value (int): The current stock count.

        Returns:
            int: The validated stock quantity.

        Constraints / Notes:
            Raises ValueError if stock quantity is negative or exceeds realistic maximum (1,000,000).
        """
        if value < 0:
            raise ValueError("Stock quantity cannot be negative.")
        if value > 1_000_000:
            raise ValueError("Stock quantity exceeds maximum allowed inventory limit (1,000,000).")
        return value

class ProductResponse(BaseModel):
    """
    Description / Purpose:
        Response schema representing a sanitized, serialized product record.

    Args / Parameters:
        id (str): Unique product identifier string.
        product_name (str): Human-readable name of the product.
        stock_quantity (int): Current available inventory count.
        unit_price (float): Price per unit.

    Returns:
        ProductResponse: Validated response instance.

    Constraints / Notes:
        Omits internal sensitive fields such as raw storage references.
    """
    id: str
    product_name: str = Field(..., min_length=1, max_length=50, strict=True)
    stock_quantity: int = Field(..., ge=0, strict=True)
    unit_price: float = Field(..., strict=True)

class ProductUpdate(BaseModel):
    """
    Description / Purpose:
        Schema for partial product updates supporting stock adjustments and detail edits.

    Args / Parameters:
        product_name (str | None): Optional updated product name.
        stock_quantity (int | None): Optional updated inventory stock count.
        unit_price (float | None): Optional updated unit price.

    Returns:
        ProductUpdate: Validated partial update schema instance.

    Constraints / Notes:
        All fields default to None. Only fields explicitly set are updated via exclude_unset=True.
    """
    product_name: str | None = Field(default=None, min_length=1, max_length=50)
    stock_quantity: int | None = Field(default=None, ge=0, le=1_000_000)
    unit_price: float | None = Field(default=None, gt=0)

    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, value: str | None) -> str | None:
        """
        Description / Purpose:
            Validates and sanitizes updated product name if provided.

        Args / Parameters:
            value (str | None): Candidate product name string.

        Returns:
            str | None: Stripped product name, or None if omitted.

        Constraints / Notes:
            Raises ValueError if a provided string is empty or only whitespace.
        """
        if value is not None:
            stripped = value.strip()
            if not stripped:
                raise ValueError("Product name cannot be empty or contain only whitespace.")
            return stripped
        return value

    @field_validator("unit_price")
    @classmethod
    def validate_unit_price(cls, value: float | None) -> float | None:
        """
        Description / Purpose:
            Validates that updated unit price is strictly positive and has at most 2 decimal places.

        Args / Parameters:
            value (float | None): Candidate unit price.

        Returns:
            float | None: Validated price rounded to 2 decimal places, or None if omitted.

        Constraints / Notes:
            Raises ValueError if value <= 0 or exceeds 2 decimal places.
        """
        if value is not None:
            if value <= 0:
                raise ValueError("Unit price must be strictly greater than zero.")
            if round(value, 2) != value:
                raise ValueError("Unit price cannot have more than 2 decimal places.")
            return round(value, 2)
        return value

    @field_validator("stock_quantity")
    @classmethod
    def validate_stock_quantity(cls, value: int | None) -> int | None:
        """
        Description / Purpose:
            Validates that updated stock count is non-negative and within allowable inventory limits.

        Args / Parameters:
            value (int | None): Candidate stock quantity.

        Returns:
            int | None: Validated stock quantity, or None if omitted.

        Constraints / Notes:
            Raises ValueError if value < 0 or value > 1,000,000.
        """
        if value is not None:
            if value < 0:
                raise ValueError("Stock quantity cannot be negative.")
            if value > 1_000_000:
                raise ValueError("Stock quantity exceeds maximum allowed inventory limit (1,000,000).")
            return value
        return value

class ProductResponse(BaseModel):
    id: str = Field(...)
    merchant_id: UUID
    stock_quantity: int = Field(..., ge=0, strict=True)
    unit_price: float = Field(..., strict=True)
    product_name: str = Field(..., min_length=1, max_length=50, strict=True)




