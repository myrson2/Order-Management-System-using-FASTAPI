from fastapi import APIRouter, Depends, HTTPException, status

from backend.dependencies import get_customer_service
from backend.schemas.Users import Customer
from backend.service.customer_service import CustomerService

from backend.dependencies import AUTH_SERVICE_URL

router = APIRouter(prefix=f"{AUTH_SERVICE_URL}/customer", tags=["Customer"])

@router.get("/")
def get_customers(service: CustomerService = Depends(get_customer_service)):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve the list of all registered customers.

    Args / Parameters:
        service (CustomerService): Injected CustomerService dependency.

    Returns:
        list[dict]: List of customer dictionaries.

    Constraints / Notes:
        Returns cached list of customers stored in memory / customer.json.
    """
    return service.get_all()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_customer(customer: Customer, service: CustomerService = Depends(get_customer_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to register and save a new customer.

    Args / Parameters:
        customer (Customer): Validated Pydantic Customer payload from HTTP request body.
        service (CustomerService): Injected CustomerService dependency.

    Returns:
        None.

    Constraints / Notes:
        Validates request body against Customer schema and appends serialized dict to storage.
    """
    print(customer.model_dump())
    service.add(customer.to_dict())

@router.get("/{customer_id}")
def get_customer_by_id(customer_id: str, service: CustomerService = Depends(get_customer_service)):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve a single customer by their unique ID string.

    Args / Parameters:
        customer_id (str): The customer ID string (UUID or legacy ID) from URL path parameter.
        service (CustomerService): Injected CustomerService dependency.

    Returns:
        dict: The matching customer record.

    Constraints / Notes:
        Raises HTTP 404 Exception if no customer matching the given ID is found.
    """
    customer = service.get_user_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

# @router.patch("/{customer_id}", status_code=status.HTTP_200_OK)
# def edit_customer_account(customer_id: str, payload: CustomerUpdate, service: CustomerService = Depends(get_customer_service)):
#     update_data = service.update_customer(customer_id, payload)
#     if not update_data:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
#     return update_data









