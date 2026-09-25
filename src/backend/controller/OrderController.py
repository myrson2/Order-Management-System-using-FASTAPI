from fastapi import APIRouter, Depends, status
from backend.dependencies import get_base_url, get_order_service
from backend.schemas.Order import OrderResponse
from backend.service import OrderService

router = APIRouter(prefix=f"{get_base_url}/order", tags=["Order"])

@router.post('/checkout/{customer_id}', status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
def checkout(customer_id: str, service: OrderService = Depends(get_order_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to process checkout for a customer's active shopping cart items.

    Args / Parameters:
        customer_id (str): Customer ID path parameter.
        service (OrderService): Injected OrderService dependency instance.

    Returns:
        OrderResponse: Validated Pydantic OrderResponse schema representing the completed order receipt.

    Constraints / Notes:
        Raises HTTP 400 Bad Request if the cart is empty or if stock is insufficient.
    """
    return service.process_checkout(customer_id)

@router.get('/customer/{customer_id}', status_code=status.HTTP_200_OK, response_model=list[dict])
def get_order_history(customer_id: str, service: OrderService = Depends(get_order_service)):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve past order receipts for a specific customer ID.

    Args / Parameters:
        customer_id (str): Customer ID path parameter.
        service (OrderService): Injected OrderService dependency instance.

    Returns:
        list[dict]: List of past order receipt dictionaries.

    Constraints / Notes:
        Returns an empty list [] if no orders match the customer_id.
    """
    return service.get_order_history(customer_id)
