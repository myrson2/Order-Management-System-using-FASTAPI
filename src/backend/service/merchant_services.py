from backend.repository.repositories import ProductRepository
from backend.schemas.Product import ProductCreate, ProductResponse
from backend.service.user_service import UserService

class MerchantService(UserService):
    """Business logic and caching service for merchant operations."""
    def __init__(self, repositories, product_repository: ProductRepository) -> None:
        """
        Description / Purpose:
            Initializes the MerchantService with user and product repositories,
            and preloads the in-memory product cache.

        Args / Parameters:
            repositories: Repository instance for merchant user data.
            product_repository (ProductRepository): Repository instance for product persistence.

        Returns:
            None.

        Constraints / Notes:
            Calls super().__init__ to set up base user caching, then populates product_cache.
        """
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

    def get_all_products(self) -> list[dict]:
        """
        Description / Purpose:
            Retrieves the full list of products currently cached in memory.

        Args / Parameters:
            None.

        Returns:
            list[dict]: List of product dictionary records from the in-memory cache.

        Constraints / Notes:
            Returns a direct reference to product_cache without database reads.
        """
        return self.product_cache

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

    def delete_product(self, product_id: str, merchant_id: str) -> ProductResponse | None:
        """
        Description / Purpose:
            Removes a product from the in-memory cache and persists the change to storage,
            ensuring the product belongs to the requesting merchant.

        Args / Parameters:
            product_id (str): Unique identifier of the product to delete.
            merchant_id (str): UUID string of the merchant requesting deletion.

        Returns:
            ProductResponse | None: ProductResponse instance of the deleted product, or None if not found/unauthorized.

        Constraints / Notes:
            Verifies both product ID and merchant ownership before mutating product_cache.
        """
        for index, products in enumerate(self.product_cache):
            if products.get('id') == product_id and str(products.get('merchant_id')) == str(merchant_id):
                deleted = self.product_cache.pop(index)
                self.save_product_cache()
                return ProductResponse(**deleted)
        return None