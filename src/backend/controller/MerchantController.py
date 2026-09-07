from fastapi import APIRouter, Depends, status
from backend.repository.repositories import MerchantRepository
from backend.schemas.Users import Merchant
from backend.service.user_services import MerchantService
from pathlib import Path
import json

target_path = Path(__file__).resolve().parent.parent / "database"
file_path = Path(target_path) / "merchant.json"

if not file_path.exists():
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump([], file)

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

@router.post("/{merchant_id}/products", status_code=status.HTTP_200_OK)
def create_a_product(merchant_id: str, service: MerchantService = Depends(get_merchant_service)):
    pass