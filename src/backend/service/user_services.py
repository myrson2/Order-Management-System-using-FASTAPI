from backend.schemas.Product import Product

class UserService:
    def __init__(self, repositories):
        self.repositories = repositories
        self.cache: list[dict] = []

    def _load_cache(self) -> None:
        """
        Description / Purpose:
            Loads customer records from repository into the in-memory cache list.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Private helper method called during initialization.
        """
        for data in self.repositories.load_repo():
            self.repositories.append(data)

    def save_cache(self) -> None:
        """
        Description / Purpose:
            Persists the in-memory customer cache list to storage via the repository.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Calls customer_repo.save_repo() with current cache contents.
        """
        json_data = [data for data in self.repositories]
        self.repositories.save_repo(json_data)

    def get_all(self):
        return self.cache

    def add(self, user_data: dict) -> None:
        self.cache.append(user_data)
        self.save_cache()

    def update(self, user_data: dict) -> None:
        for i, c in enumerate(self.cache):
            if str(c.get("id")) == str(user_data.get('id')):
                self.cache[i] = user_data
                self.save_cache()
                break

class CustomerService(UserService):
    """Business logic and caching service for customer operations."""

class MerchantService(UserService):
    """Business logic and caching service for merchant operations."""

    def add_product(self, product: Product):
        pass

class OrderService:
    """Business logic service for managing order transactions."""

    def __init__(self, order_repo) -> None:
        """
        Description / Purpose:
            Initializes OrderService with an OrderRepository dependency.

        Args / Parameters:
            order_repo: Order data access repository instance.

        Returns:
            None.

        Constraints / Notes:
            Stores repository reference for order operations.
        """
        self.order_repo = order_repo









