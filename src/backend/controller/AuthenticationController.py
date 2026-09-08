from fastapi import APIRouter, Depends, HTTPException, status
from backend.dependencies import AUTH_SERVICE_URL, get_auth_service
from backend.schemas.Users.User import UserLogin, UserResponse

from backend.service.authentication_service import AuthenticationService
router = APIRouter(prefix=AUTH_SERVICE_URL, tags=["Authentication"])

@router.post("/login")
def get_login_in(user: UserLogin, service: AuthenticationService = Depends(get_auth_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to authenticate user credentials and transition active status to online.

    Args / Parameters:
        user (UserLogin): Validated login payload containing user email and password.
        service (AuthenticationService): Injected AuthenticationService singleton.

    Returns:
        UserResponse: Authenticated customer or merchant response DTO.

    Constraints / Notes:
        Raises HTTP 401 UNAUTHORIZED if matching credentials are not found in storage caches.
    """
    account = service.login(user)
    if account is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return account

@router.post("/logout")
def get_logout(user: UserResponse, service: AuthenticationService = Depends(get_auth_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to terminate a user session and transition active status to offline.

    Args / Parameters:
        user (UserResponse): DTO representing the active user session requesting logout.
        service (AuthenticationService): Injected AuthenticationService singleton.

    Returns:
        dict: Confirmation message payload {"message": "Successfully logged out"}.

    Constraints / Notes:
        Raises HTTP 400 BAD REQUEST if logout operation or cache update fails.
    """
    success = service.logout(user)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed")
    return {"message": "Successfully logged out"}