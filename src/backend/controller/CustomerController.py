from backend.schemas import Customer
from fastapi import APIRouter, Depends, HTTPException, status
from backend.repository.repositories import CustomerRepository
from backend.service.services import CustomerService
from backend.schemas.Customer import Customer
from pathlib import Path

target_path = Path(__file__).resolve().parent.parent / "database" / "customer.json"
customer_repository = CustomerRepository(target_path)
customer_service = CustomerService(customer_repository)

def get_customer_service() -> CustomerService:
    return customer_service

router = APIRouter(prefix="/api/v1/customer", tags=["Customer"])

@router.get("/")
def get_customers(service: CustomerService = Depends(get_customer_service)):
    return service.get_customers()

@router.get("/{customer_id}")
def get_customer_by_id(customer_id: int, service: CustomerService = Depends(get_customer_service)):
    customer = service.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_customer(customer: Customer, service: CustomerService = Depends(get_customer_service)):
    service.add_customer(customer.to_dict())
