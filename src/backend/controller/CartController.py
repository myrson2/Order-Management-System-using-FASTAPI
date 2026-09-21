from fastapi import APIRouter, Depends, status
from backend.dependencies import get_base_url, get_order_service
from backend.schemas.Cart import CartCreate, CartResponse
from backend.schemas.Product import ProductResponse
from backend.service import OrderService

router = APIRouter(prefix=f"{get_base_url}/cart", tags=["Order"])

@router.post('/customer/{customer_id}/add', status_code=status.HTTP_201_CREATED, response_model=CartResponse)
def add_order(customer_id: str, cart: CartCreate, service: OrderService = Depends(get_order_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to add a product item to a customer's shopping cart.

    Args / Parameters:
        customer_id (str): Customer ID path parameter.
        cart (CartCreate): Validated Pydantic CartCreate request body payload.
        service (OrderService): Injected OrderService dependency instance.

    Returns:
        CartResponse: Serialized CartResponse schema of the saved cart item.

    Constraints / Notes:
        Returns status 201 Created upon successful persistence into cart.json.
    """
    return service.add_to_cart(cart)

@router.get('/customer/{customer_id}/view', status_code=status.HTTP_200_OK, response_model=list[dict])
def view_cart(customer_id: str, service: OrderService = Depends(get_order_service)):
    """
    Description / Purpose:
        HTTP GET endpoint to fetch all active cart items for a specific customer ID.

    Args / Parameters:
        customer_id (str): Customer ID path parameter.
        service (OrderService): Injected OrderService dependency instance.

    Returns:
        list[dict]: List of cart item dictionaries for the specified customer.

    Constraints / Notes:
        Returns empty list [] if no items match the customer ID.
    """
    return service.view_my_cart(customer_id)

@router.get('/customer/{customer_id}/product/{product_id}', status_code=status.HTTP_200_OK, response_model=ProductResponse)
def get_product(customer_id: str, product_id: str, merchant_id: str, service: OrderService = Depends(get_order_service)):
    return service.get_product_by_id(product_id, merchant_id)