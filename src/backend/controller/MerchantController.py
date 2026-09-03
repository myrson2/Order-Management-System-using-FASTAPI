from fastapi import APIRouter, Depends, HTTPException, status
from backend.repository.repositories import CustomerRepository, MerchantRepository
from backend.schemas.Users import Customer, Merchant
from backend.service.UserServices.user_services import MerchantService
from pathlib import Path

target_path = Path(__file__).resolve().parent.parent / "database"
file_path = Path(target_path) / "merchant.json"
merchant_repository = MerchantRepository(file_path)
merchant_service = MerchantService(merchant_repository)

def get_merchant_service() -> MerchantService:
    return merchant_service

router = APIRouter(prefix="/api/v1/merchant", tags=["Merchant"])

@router.get("/")
def get_users(service: MerchantService = Depends(get_merchant_service)):
    return service.get_merchants()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_merchant(merchant: Merchant, service: MerchantService = Depends(get_merchant_service)):
    print(merchant.model_dump())
    service.add_merchant(merchant.to_dict())