from typing import TypeVar
from backend.schemas.Users import Customer, Merchant
from backend.schemas.Users.Customer import CustomerResponse
from backend.schemas.Users.Merchant import MerchantResponse
from backend.schemas.Users.User import UserLogin, UserResponse, EnumType
from backend.service.customer_service import CustomerService
from backend.service.merchant_services import MerchantService

T = TypeVar("T", Customer, Merchant)

def _find_user_in_repo(repo: list[dict], email: str, password: str, model_class: type[T]) -> T | None:
    """
    Description / Purpose:
        Searches an in-memory repository cache list for matching email and password,
        and returns an instantiated model instance if found.

    Args / Parameters:
        repo (list[dict]): The in-memory cache list of user dictionaries.
        email (str): The email address to look for.
        password (str): The plain-text password to compare against.
        model_class (type[T]): The target Pydantic class to instantiate (Customer or Merchant).

    Returns:
        T | None: Instantiated model instance if match is found, or None.

    Constraints / Notes:
        Compares plain text credentials; relies on model_class.from_dict for instantiation.
    """
    if not repo:
        return None

    match = next(
        (item for item in repo if item.get("email") == email and item.get("password") == password),
        None
    )
    return model_class.from_dict(match) if match else None

class AuthenticationService:
    """Handles authentication lifecycle, status toggling, and user session validation."""

    def __init__(self, customer_service: CustomerService, merchant_service: MerchantService) -> None:
        """
        Description / Purpose:
            Initializes AuthenticationService with customer and merchant domain service dependencies.

        Args / Parameters:
            customer_service (CustomerService): Customer service managing customer records and cache.
            merchant_service (MerchantService): Merchant service managing merchant records and cache.

        Returns:
            None.

        Constraints / Notes:
            Stores references for user lookups and active status updates across domains.
        """
        self.customer_service = customer_service
        self.merchant_service = merchant_service

    def login(self, user: UserLogin) -> UserResponse | None:
        """
        Description / Purpose:
            Authenticates user credentials against customer and merchant caches, sets
            the matched user's active status to online, and returns safe UserResponse DTO.

        Args / Parameters:
            user (UserLogin): Validated login payload containing email and password.

        Returns:
            UserResponse | None: Safe response model (CustomerResponse or MerchantResponse) or None if invalid.

        Constraints / Notes:
            Searches customer cache first, then merchant cache. Persists updated online status.
        """
        email = user.email
        password = user.password

        # Check customer
        customer = _find_user_in_repo(self.customer_service.cache, email, password, Customer)
        if customer is not None:
            customer.online()
            self.customer_service.update(customer.to_dict())
            return CustomerResponse(**customer.model_dump())

        # Check merchant
        merchant = _find_user_in_repo(self.merchant_service.cache, email, password, Merchant)
        if merchant is not None:
            merchant.online()
            self.merchant_service.update(merchant.to_dict())
            return MerchantResponse(**merchant.model_dump())

        return None

    def logout(self, user_res: UserResponse) -> bool:
        """
        Description / Purpose:
            Logs out an authenticated user by locating their record, setting active_status
            to OFFLINE, and persisting the updated state.

        Args / Parameters:
            user_res (UserResponse): DTO representing the currently logged-in user.

        Returns:
            bool: True if user was found and updated to offline, False otherwise.

        Constraints / Notes:
            Validates user_type against EnumType explicitly. Returns False if user ID is missing.
        """
        user_id_str = str(user_res.id)

        if user_res.user_type == EnumType.MERCHANT:
            raw_data = self.merchant_service.get_user_by_id(user_id_str)
            if not raw_data:
                return False
            merchant = Merchant.from_dict(raw_data)
            merchant.offline()
            self.merchant_service.update(merchant.to_dict())
            return True

        elif user_res.user_type == EnumType.CUSTOMER:
            raw_data = self.customer_service.get_user_by_id(user_id_str)
            if not raw_data:
                return False
            customer = Customer.from_dict(raw_data)
            customer.offline()
            self.customer_service.update(customer.to_dict())
            return True

        return False

