import os
from fastapi import APIRouter, Depends, HTTPException, status
from backend.schemas.Users.User import UserLogin
from backend.service.UserServices.user_services import AuthenticationService

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
AUTH_SERVICE_URL = f"{API_BASE_URL}/auth"
CUSTOMER_URL = f"{API_BASE_URL}/customer"
MERCHANT_URL = f"{API_BASE_URL}/merchant"

router = APIRouter(prefix=AUTH_SERVICE_URL, tags=["Authentication"])

def get_auth_service() -> AuthenticationService:
    return authentication_service

@router.get("/login")
def get_login_in(user: UserLogin, service: AuthenticationService = Depends(get_auth_service)):
    account = service.login(user)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return account