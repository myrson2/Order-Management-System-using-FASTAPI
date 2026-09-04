import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from backend.repository.repositories import CustomerRepository, MerchantRepository
from backend.schemas.Users.User import UserLogin
from backend.service.UserServices.user_services import AuthenticationService, CustomerService, MerchantService

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
AUTH_SERVICE_URL = f"/api/v1/auth"
target_path = Path(__file__).resolve().parent.parent / "database"
customer_repo = CustomerRepository(target_path / "customer.json")
merchant_repo = MerchantRepository(target_path / "merchant.json")
customer_service = CustomerService(customer_repo)
merchant_service = MerchantService(merchant_repo)

authentication_service = AuthenticationService(customer_service, merchant_service)

router = APIRouter(prefix=AUTH_SERVICE_URL, tags=["Authentication"])

def get_auth_service() -> AuthenticationService:
    return authentication_service

@router.post("/login")
def get_login_in(user: UserLogin, service: AuthenticationService = Depends(get_auth_service)):
    account = service.login(user)
    if account is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return account