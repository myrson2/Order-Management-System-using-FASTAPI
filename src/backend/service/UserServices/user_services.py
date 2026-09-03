import httpx

from backend.repository.repositories import CustomerRepository, MerchantRepository
from backend.schemas.Users import Customer, Merchant, User
from backend.schemas.Users.Customer import CustomerResponse
from backend.schemas.Users.Merchant import MerchantResponse
from backend.schemas.Users.User import UserLogin, UserResponse


class CustomerService:
    """Business logic and caching service for customer operations."""

    def __init__(self, customer_repo: CustomerRepository) -> None: 
        """
        Description / Purpose:
            Initializes CustomerService with a CustomerRepository dependency and loads initial cache.

        Args / Parameters:
            customer_repo (CustomerRepository): Customer data access repository.

        Returns:
            None.

        Constraints / Notes:
            Populates in-memory cache upon initialization.
        """
        self.customer_repo = customer_repo
        self.customer_cache: list[dict] = []
        self._load_customer_cache()

    def _load_customer_cache(self) -> None: 
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
        for customer_data in self.customer_repo.load_repo():
            self.customer_cache.append(customer_data)

    def save_customer_cache(self) -> None:
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
        json_data = [customer for customer in self.customer_cache]
        self.customer_repo.save_repo(json_data)

    def get_customers(self) -> list[dict]:
        """
        Description / Purpose:
            Retrieves the full list of cached customer dictionaries.

        Args / Parameters:
            None.

        Returns:
            list[dict]: List of customer dictionaries in memory.

        Constraints / Notes:
            Returns direct reference to in-memory customer cache.
        """
        return self.customer_cache

    def add_customer(self, customer_data: dict) -> None:
        """
        Description / Purpose:
            Appends a new customer record to cache and saves to persistent storage.

        Args / Parameters:
            customer_data (dict): Serialized customer dictionary payload.

        Returns:
            None.

        Constraints / Notes:
            Updates in-memory cache and triggers immediate save to storage.
        """
        self.customer_cache.append(customer_data)
        self.save_customer_cache()

    def get_customer_by_id(self, customer_id: str) -> dict | None:
        """
        Description / Purpose:
            Searches for a customer in cache by matching unique ID string.

        Args / Parameters:
            customer_id (str): Customer UUID string to search for.

        Returns:
            dict | None: The matching customer dictionary if found, or None.

        Constraints / Notes:
            Compares string representation of ID fields.
        """
        customers = self.get_customers()
        for c in customers:
            if str(c.get("id")) == str(customer_id):
                return c
        return None

class MerchantService:
    """Business logic and caching service for merchant operations."""

    def __init__(self, merchant_repo: MerchantRepository) -> None:
        """
        Description / Purpose:
            Initializes MerchantService with a MerchantRepository dependency and loads cache.

        Args / Parameters:
            merchant_repo (MerchantRepository): Merchant data access repository.

        Returns:
            None.

        Constraints / Notes:
            Loads merchant cache upon initialization.
        """
        self.merchant_repo = merchant_repo
        self.merchant_cache: list[dict] = []
        self._load_merchant_cache()

    def _load_merchant_cache(self) -> None:
        """
        Description / Purpose:
            Loads merchant records from repository into the in-memory cache.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Private helper method.
        """
        for merchant_data in self.merchant_repo.load_repo():
            self.merchant_cache.append(merchant_data)

    def save_merchant_cache(self) -> None:
        """
        Description / Purpose:
            Persists in-memory merchant cache list to storage.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Calls merchant_repo.save_repo() with current cache.
        """
        json_data = [merchant for merchant in self.merchant_cache]
        self.merchant_repo.save_repo(json_data)

    def get_merchants(self) -> list[dict]:
        """
        Description / Purpose:
            Retrieves the full list of cached merchant dictionaries.

        Args / Parameters:
            None.

        Returns:
            list[dict]: List of merchant dictionaries in memory.

        Constraints / Notes:
            Returns in-memory merchant cache list.
        """
        return self.merchant_cache

    def add_merchant(self, merchant_data: dict) -> None:
        """
        Description / Purpose:
            Appends a new merchant record to cache and saves to storage.

        Args / Parameters:
            customer_data (dict): Serialized merchant dictionary payload.

        Returns:
            None.

        Constraints / Notes:
            Appends to merchant_cache and triggers save_merchant_cache().
        """
        self.merchant_cache.append(merchant_data)
        self.save_merchant_cache()

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


def _find_user_in_repo(repo, email: str, password: str, model_class):
    """Helper to search a repository and return the instantiated model if found."""
    if not repo:
        return None

    match = next(
        (item for item in repo if item.get("email") == email and item.get("password") == password),
        None
    )
    return model_class.from_dict(match) if match else None


class AuthenticationService:
    def __init__(self, customer_repo: CustomerRepository, merchant_repo: MerchantRepository) -> None:
        """
        Description / Purpose:
            Initializes UserInterface with target API endpoints for customer and merchant operations.

        Args / Parameters:
            customer_url (str): API endpoint URL for customer routes.
            merchant_url (str): API endpoint URL for merchant routes.

        Returns:
            None.

        Constraints / Notes:
            Stores URLs for HTTP client requests via httpx.
        """
        self.customer_repo = customer_repo
        self.merchant_repo = merchant_repo

    def login(self, user: UserLogin) -> UserResponse | None:
        email = user.email
        password = user.password

        # Check customer repository independently
        if customer := _find_user_in_repo(self.customer_repo.load_repo(), email, password, Customer):
            return CustomerResponse(**customer.model_dump())

        # Check merchant repository independently
        if merchant := _find_user_in_repo(self.merchant_repo.load_repo(), email, password, Merchant):
            return MerchantResponse(**merchant.model_dump())

        return None

    def logout(self):
        pass
