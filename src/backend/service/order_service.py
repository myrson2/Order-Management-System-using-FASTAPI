from backend.schemas.Cart import CartCreate, CartResponse


class OrderService:
    """Business logic service for managing order transactions."""

    def __init__(self, cart_repo) -> None:
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

    def add_to_cart(self, cart: CartCreate) -> CartResponse:
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
        self.cart_cache.append(cart_dict)
        self.save_cart_cache()
        return CartResponse(**cart_dict)

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

