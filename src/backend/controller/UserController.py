from fastapi import APIRouter, Depends, HTTPException, status
from backend.repository.repositories import CustomerRepository
from backend.service.UserServices.user_services import CustomerService
from backend.schemas.Users.User import UserCreate, CustomerUpdate, Customer
from pathlib import Path

target_path = Path(__file__).resolve().parent.parent / "database"
file_path = Path(target_path) / "customer.json"
customer_repository = CustomerRepository(target_path)
customer_service = CustomerService(customer_repository)

def get_customer_service() -> CustomerService:
    return customer_service

router = APIRouter(prefix="/api/v1/customer", tags=["Customer"])

@router.get("/")
def get_customers(service: CustomerService = Depends(get_customer_service)):
    return service.get_customers()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_customer(customer: UserCreate, service: CustomerService = Depends(get_customer_service)):
    service.add_customer(customer.to_dict())

@router.get("/{customer_id}")
def get_customer_by_id(customer_id: int, service: CustomerService = Depends(get_customer_service)):
    customer = service.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer



@router.patch("/{customer_id}", status_code=status.HTTP_200_OK)
def edit_customer_account(customer_id: str, payload: CustomerUpdate, service: CustomerService = Depends(get_customer_service)):
    update_data = service.update_customer(customer_id, payload)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return update_data









