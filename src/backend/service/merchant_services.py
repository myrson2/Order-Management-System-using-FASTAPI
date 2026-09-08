from backend.schemas.Product import Product
from backend.service.user_service import UserService


class MerchantService(UserService):
    """Business logic and caching service for merchant operations."""

    def add_product(self, product: Product) -> None:
        """
        Description / Purpose:
            Appends a new product to the merchant's catalog and persists changes.

        Args / Parameters:
            product (Product): Validated Product schema instance.

        Returns:
            None.

        Constraints / Notes:
            Stub method awaiting full merchant-to-product relationship implementation.
        """
        pass