from backend.schemas.Users import Customer, Merchant
from backend.schemas.Users.Customer import CustomerResponse
from backend.schemas.Users.Merchant import MerchantResponse
from backend.schemas.Users.User import UserLogin, UserResponse, EnumType
from backend.service.user_services import CustomerService, MerchantService

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
    def __init__(self, customer_service: CustomerService, merchant_service: MerchantService) -> None:
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
        self.customer_service = customer_service
        self.merchant_service = merchant_service

    def login(self, user: UserLogin) -> UserResponse | None:
        email = user.email
        password = user.password

        # Check customer repository independently
        if customer := _find_user_in_repo(self.customer_service.customer_cache, email, password, Customer):
            customer.online()
            self.customer_service.update_customer(customer.to_dict())
            return CustomerResponse(**customer.model_dump())

        # Check merchant repository independently
        if merchant := _find_user_in_repo(self.merchant_service.merchant_cache, email, password, Merchant):
            merchant.online()
            self.merchant_service.update_merchant(merchant.to_dict())
            return MerchantResponse(**merchant.model_dump())

        return None

    def logout(self, user_res: UserResponse) -> bool:
        # Check the enum type
        # get the right cache based on enum type
        # get the details based on id
        # then change status to offline
        #save to cache and repository
        if user_res.user_type == EnumType.MERCHANT.value:
            merchant = Merchant.from_dict(self.merchant_service.get_merchant_by_id(str(user_res.id)))
            merchant.offline()
            self.merchant_service.update_merchant(merchant.to_dict())
            status = True
        else:
            customer = Customer.from_dict(self.customer_service.get_customer_by_id(str(user_res.id)))
            customer.offline()
            self.customer_service.update_customer(customer.to_dict())
            status = True

        return status

