from fastapi import APIRouter, Depends, HTTPException, status

from backend.dependencies import get_merchant_service, get_base_url
from backend.schemas.Product import ProductCreate, ProductResponse, ProductUpdate
from backend.schemas.Users import Merchant
from backend.service.merchant_services import MerchantService

router = APIRouter(prefix=f"{get_base_url}/merchant", tags=["Merchant"])

@router.get("/")
def get_users(
        service: MerchantService = Depends(get_merchant_service)
):
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
def create_merchant(
        merchant: Merchant,
        service: MerchantService = Depends(get_merchant_service)
):
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
def create_a_product(
        merchant_id: str,
        prd: ProductCreate,
        service: MerchantService = Depends(get_merchant_service)
):
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
    service.add_product(prd)

@router.get("/products", status_code=status.HTTP_200_OK)
def get_all_products(
        service: MerchantService = Depends(get_merchant_service)
) -> list[dict]:
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve the full catalog of products across all merchants.

    Args / Parameters:
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        list[Any]: List of product dictionaries from the in-memory product cache.

    Constraints / Notes:
        Returns an empty list if no products exist in the catalog.
    """
    all_products = service.get_all_products()
    if len(all_products) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empty list of products."
        )
    return all_products

@router.delete("/{merchant_id}/products/{product_id}", status_code=status.HTTP_200_OK)
def delete_a_product(
    merchant_id: str,
    product_id: str,
    service: MerchantService = Depends(get_merchant_service)
):
    """
    Description / Purpose:
        HTTP DELETE endpoint to remove a specific product from a merchant's inventory.

    Args / Parameters:
        merchant_id (str): Unique merchant UUID string from URL path parameter.
        product_id (str): Unique product ID string from URL path parameter.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        ProductResponse: Serialized ProductResponse model of the deleted product.

    Constraints / Notes:
        Raises HTTP 404 HTTPException if the product ID does not exist in the inventory.
    """
    del_product = service.delete_product(product_id, merchant_id)
    if not del_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product matches ID '{product_id}'."
        )
    return del_product

@router.get("/{merchant_id}/products/{product_id}", status_code=status.HTTP_200_OK)
def get_a_product_using_id(
    merchant_id: str,
    product_id: str,
    service: MerchantService = Depends(get_merchant_service)
):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve details of a specific product by its ID under a merchant catalog.

    Args / Parameters:
        merchant_id (str): Unique merchant UUID string from URL path parameter.
        product_id (str): Unique product ID string from URL path parameter.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        dict: Product record dictionary matching the provided ID.

    Constraints / Notes:
        Raises HTTP 404 HTTPException if the product ID does not exist in storage.
    """
    that_product = service.get_product_by_id(product_id)
    if not that_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product matches ID '{product_id}'."
        )
    return that_product

@router.patch("/{merchant_id}/products/{product_id}/restock", status_code=status.HTTP_200_OK)
def restock_product_endpoint(
    merchant_id: str,
    product_id: str,
    product_update: ProductUpdate,
    service: MerchantService = Depends(get_merchant_service)
):
    """
    Description / Purpose:
        HTTP PATCH endpoint to update the stock count of a specific merchant's product.

    Args / Parameters:
        merchant_id (str): Unique merchant UUID string from URL path parameter.
        product_id (str): Unique product ID string from URL path parameter.
        product_update (ProductUpdate): Validated update schema containing modified attributes.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        dict: The updated product record dictionary.

    Constraints / Notes:
        Raises HTTP 404 HTTPException if the product ID does not exist in inventory.
    """
    updated_product = service.update_product(product_id, product_update)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product matches ID '{product_id}'."
        )
    return updated_product

@router.patch("/{merchant_id}/products/{product_id}/deduct", status_code=status.HTTP_200_OK)
def deduct_product_endpoint(
    merchant_id: str,
    product_id: str,
    product_update: ProductUpdate,
    service: MerchantService = Depends(get_merchant_service)
):
    """
    Description / Purpose:
        HTTP PATCH endpoint to update the stock count of a specific merchant's product.

    Args / Parameters:
        merchant_id (str): Unique merchant UUID string from URL path parameter.
        product_id (str): Unique product ID string from URL path parameter.
        product_update (ProductUpdate): Validated update schema containing modified attributes.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        dict: The updated product record dictionary.

    Constraints / Notes:
        Raises HTTP 404 HTTPException if the product ID does not exist in inventory.
    """
    updated_product = service.update_product(product_id, product_update)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product matches ID '{product_id}'."
        )
    return updated_product

@router.patch("/{merchant_id}/products/{product_id}/edit", status_code=status.HTTP_200_OK)
def edit_product_endpoint(
    merchant_id: str,
    product_id: str,
    product_update: ProductUpdate,
    service: MerchantService = Depends(get_merchant_service)
):
    """
    Description / Purpose:
        HTTP PATCH endpoint to edit non-stock details (name and unit price) of a specific merchant product.

    Args / Parameters:
        merchant_id (str): Unique merchant UUID string from URL path parameter.
        product_id (str): Unique product ID string from URL path parameter.
        product_update (ProductUpdate): Validated update schema containing new name and/or unit price.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        dict: The updated product record dictionary.

    Constraints / Notes:
        Raises HTTP 404 HTTPException if the product ID is not found in inventory.
    """
    updated_product = service.update_product(product_id, product_update)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product matches ID '{product_id}'."
        )
    return updated_product