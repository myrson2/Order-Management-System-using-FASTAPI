from backend.repository.repositories import ProductRepository
from backend.schemas.Product import ProductCreate
from backend.service.user_service import UserService

class MerchantService(UserService):
    """Business logic and caching service for merchant operations."""
    def __init__(self, repositories, product_repository: ProductRepository) -> None:
        super().__init__(repositories)
        self.product_repository = product_repository
        self.product_cache: list[dict] = []
        self._load_product_cache()

    def _load_product_cache(self) -> None:
        """
        Description / Purpose:
            Loads entity records from the repository into the in-memory cache list.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Private helper method called during initialization to populate cache.
        """
        for data in self.product_repository.load_repo():
            self.product_cache.append(data)

    def save_product_cache(self) -> None:
        """
        Description / Purpose:
            Persists the in-memory cache list to storage via the underlying repository.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Calls repositories.save_repo() with a snapshot of the current cache contents.
        """
        json_data_products = [products for products in self.product_cache]
        self.product_repository.save_repo(json_data_products)

    def add_product(self, product: ProductCreate) -> None:
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

        self.product_cache.append(product.to_dict())
        self.save_product_cache()