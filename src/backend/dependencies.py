import json
import os
from pathlib import Path

from backend.repository.repositories import CustomerRepository, MerchantRepository, ProductRepository
from backend.service.authentication_service import AuthenticationService
from backend.service.customer_service import CustomerService
from backend.service.merchant_services import MerchantService

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001/api/v1")
AUTH_SERVICE_URL = f"/api/v1/auth"
get_base_url = f"/api/v1"

print(API_BASE_URL)

target_path = Path(__file__).resolve().parent / "database"
customer_path = target_path / "customer.json"
merchant_path = target_path / "merchant.json"
product_path = target_path / "product.json"

if not customer_path.exists():
    with open(customer_path, "w", encoding="utf-8") as file:
        json.dump([], file)

if not merchant_path.exists():
    with open(merchant_path, "w", encoding="utf-8") as file:
        json.dump([], file)

if not product_path.exists():
    with open(product_path, "w", encoding="utf-8") as file:
        json.dump([], file)

customer_repo = CustomerRepository(customer_path)
merchant_repo = MerchantRepository(merchant_path)
product_repo = ProductRepository(product_path)

customer_service = CustomerService(customer_repo)
merchant_service = MerchantService(merchant_repo, product_repo)

authentication_service = AuthenticationService(customer_service, merchant_service)

def get_auth_service() -> AuthenticationService:
    """
    Description / Purpose:
        FastAPI dependency provider returning the singleton instance of AuthenticationService.

    Args / Parameters:
        None.

    Returns:
        AuthenticationService: Shared authentication service instance.

    Constraints / Notes:
        Used with FastAPI Depends() dependency injection in authentication controller routes.
    """
    return authentication_service

def get_customer_service() -> CustomerService:
    """
    Description / Purpose:
        FastAPI dependency provider returning the singleton instance of CustomerService.

    Args / Parameters:
        None.

    Returns:
        CustomerService: Shared customer service instance.

    Constraints / Notes:
        Used with FastAPI Depends() dependency injection in controller routes.
    """
    return customer_service

def get_merchant_service() -> MerchantService:
    """
    Description / Purpose:
        FastAPI dependency provider returning the singleton instance of MerchantService.

    Args / Parameters:
        None.

    Returns:
        MerchantService: Shared merchant service instance.

    Constraints / Notes:
        Used with FastAPI Depends() dependency injection in controller routes.
    """
    return merchant_service