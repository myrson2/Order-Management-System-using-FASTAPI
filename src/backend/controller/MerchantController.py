from fastapi import APIRouter, Depends, status

from backend.dependencies import get_merchant_service, AUTH_SERVICE_URL
from backend.schemas.Users import Merchant
from backend.service.merchant_services import MerchantService

router = APIRouter(prefix=f"{AUTH_SERVICE_URL}/merchant", tags=["Merchant"])

@router.get("/")
def get_users(service: MerchantService = Depends(get_merchant_service)):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve the full list of registered merchants.

    Args / Parameters:
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        list[dict]: List of merchant dictionaries from cache / merchant.json.

    Constraints / Notes:
        Returns all records currently in memory without pagination.
    """
    return service.get_all()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_merchant(merchant: Merchant, service: MerchantService = Depends(get_merchant_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to register and persist a new merchant account.

    Args / Parameters:
        merchant (Merchant): Validated Merchant Pydantic schema from request body.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        None.

    Constraints / Notes:
        Appends serialized record to memory and synchronously writes to merchant.json.
    """
    print(merchant.model_dump())
    service.add(merchant.to_dict())

@router.post("/{merchant_id}/products", status_code=status.HTTP_200_OK)
def create_a_product(merchant_id: str, service: MerchantService = Depends(get_merchant_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to add a new product under a specific merchant's catalog.

    Args / Parameters:
        merchant_id (str): Unique merchant UUID string from URL path parameter.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        None.

    Constraints / Notes:
        Route stub awaiting inventory processing implementation.
    """
    pass