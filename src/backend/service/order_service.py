from fastapi import HTTPException
from starlette import status

from backend.schemas.Cart import CartCreate, CartResponse, CartUpdate
from backend.schemas.Product import ProductResponse


class OrderService:
    """Business logic service for managing order transactions."""

    def __init__(self, cart_repo, product_repo) -> None:
        """
        Description / Purpose:
            Initializes OrderService with a CartRepository dependency and populates the cart cache.

        Args / Parameters:
            cart_repo: Cart data access repository instance.

        Returns:
            None.

        Constraints / Notes:
            Stores repository reference and invokes _load_cart_cache() to load persistent records.
        """
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.cart_cache: list[dict] = []
        self._load_cart_cache()

    def _load_cart_cache(self) -> None:
        """
        Description / Purpose:
            Loads entity records from the repository into the in-memory cache list.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Private helper method called during initialization to populate cache.
        """
        for data in self.cart_repo.load_repo():
            self.cart_cache.append(data)

    def save_cart_cache(self) -> None:
        """
        Description / Purpose:
            Persists the in-memory cache list to storage via the underlying repository.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Calls repositories.save_repo() with a snapshot of the current cache contents.
        """
        json_data = [data for data in self.cart_cache]
        self.cart_repo.save_repo(json_data)

    def get_cart_by_id(self,
                       cart_id: str,
                       customer_id: str
                        ) -> CartResponse | None:
        """
        Description / Purpose:
            Searches the in-memory product cache for a product matching the given ID.

        Args / Parameters:
            product_id (str): Unique product identifier string to look up.

        Returns:
            dict | None: The matching product dictionary if found, or None.

        Constraints / Notes:
            Scans product_cache linearly by key 'id'.
        """
        cart_item = None
        for index, cart in enumerate(self.cart_repo.load_repo()):
            if cart.get('id') == cart_id and str(cart.get('customer_id')) == str(customer_id):
                cart_item = CartResponse(**cart)

        if cart_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product ID ({cart_id}) not found."
            )
        return cart_item

    def get_product_by_id(self,
                          product_id: str,
                          merchant_id: str
                        ) -> ProductResponse | None:
        """
        Description / Purpose:
            Searches the in-memory product cache for a product matching the given ID.

        Args / Parameters:
            product_id (str): Unique product identifier string to look up.

        Returns:
            dict | None: The matching product dictionary if found, or None.

        Constraints / Notes:
            Scans product_cache linearly by key 'id'.
        """
        prd_item = None
        for index, product in enumerate(self.product_repo.load_repo()):
            if product.get('id') == product_id and str(product.get('merchant_id')) == str(merchant_id):
                prd_item = ProductResponse(**product)

        if prd_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product ID ({product_id}) not found."
            )
        return prd_item

    def validate_quantity(self, quantity: int, merchant_id: str) -> bool:
        for products in self.product_repo.load_repo():
            if products['merchant_id'] != merchant_id:
                continue
            else:
                if products['stock_quantity'] < quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Requested quantity ({quantity}) exceeds available stock ({products['stock_quantity']})."
                    )
                return True
        return False

    def add_to_cart(self, cart: CartCreate) -> CartResponse | None:
        """
        Description / Purpose:
            Appends a new cart item to the in-memory cache and persists it to JSON storage.

        Args / Parameters:
            cart (CartCreate): Validated Pydantic schema containing cart item details.

        Returns:
            CartResponse: Serialized CartResponse model matching the added cart item.

        Constraints / Notes:
            Serializes model to JSON-compatible dictionary before cache storage.
        """
        cart_dict = cart.model_dump(mode='json')
        if self.validate_quantity(cart_dict['quantity'], cart_dict['merchant_id']):
            self.cart_cache.append(cart_dict)
            self.save_cart_cache()
            return CartResponse(**cart_dict)
        else:
            return None

    def view_my_cart(self, customer_id: str) -> list[dict]:
        """
        Description / Purpose:
            Retrieves all active cart items belonging to a specific customer ID.

        Args / Parameters:
            customer_id (str): Unique customer identifier string.

        Returns:
            list[dict]: List of cart dictionaries matching the customer ID.

        Constraints / Notes:
            Filters the in-memory cart_cache list by customer_id.
        """
        cart = [data for data in self.cart_cache if data['customer_id'] == customer_id]
        return cart

    def update_cart_item(self, customer_id: str, cart_id: str, payload: CartUpdate) -> CartResponse | None:
        """
        Description / Purpose:
            Updates specific fields of an existing cart item in cache and persists changes to JSON storage.

        Args / Parameters:
            customer_id (str): Customer ID associated with the cart item.
            cart_id (str): Unique cart item primary key ID string.
            payload (CartUpdate): Validated Pydantic schema containing partial fields to update.

        Returns:
            CartResponse | None: Updated CartResponse object if found and modified, or None.

        Constraints / Notes:
            Uses model_dump(exclude_unset=True) for PATCH semantics to update only specified fields.
        """
        for item in self.cart_cache:
            if str(item.get('id')) == str(cart_id) and str(item.get('customer_id')) == str(customer_id):
                update_data = payload.model_dump(exclude_unset=True)
                item.update(update_data)
                self.save_cart_cache()
                return CartResponse(**item)
        return None

    def delete_cart_item(self, customer_id: str, cart_id: str) -> CartResponse | None:
        """
        Description / Purpose:
            Removes a specific cart item matching cart_id and customer_id from cache and persistent disk storage.

        Args / Parameters:
            customer_id (str): Customer ID associated with the cart item.
            cart_id (str): Unique cart item primary key ID string.

        Returns:
            CartResponse | None: Deleted CartResponse object if found and removed, or None.

        Constraints / Notes:
            Mutates self.cart_cache in-place and calls save_cart_cache().
        """
        for item in self.cart_cache:
            if str(item.get('id')) == str(cart_id) and str(item.get('customer_id')) == str(customer_id):
                self.cart_cache.remove(item)
                self.save_cart_cache()
                return CartResponse(**item)
        return None

    def checkout(self, cart_id: str) -> OrderResponse:

