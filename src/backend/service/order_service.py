from fastapi import HTTPException
from starlette import status

from backend.schemas.Cart import CartCreate, CartResponse, CartUpdate
from backend.schemas.Order import OrderResponse
from backend.schemas.OrderItems import OrderItem
from backend.schemas.Product import ProductResponse


class OrderService:
    """Business logic service for managing order transactions."""

    def __init__(self, cart_repo, product_repo, order_repo) -> None:
        """
        Description / Purpose:
            Initializes OrderService with CartRepository, ProductRepository, and OrderRepository dependencies.

        Args / Parameters:
            cart_repo: Cart data access repository instance.
            product_repo: Product inventory repository instance.
            order_repo: Order receipts repository instance.

        Returns:
            None.

        Constraints / Notes:
            Stores repository references and populates cart_cache and order_cache on initialization.
        """
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.cart_cache: list[dict] = []
        self.order_cache: list[dict] = []
        self._load_cart_cache()
        self._load_order_cache()

    def _load_cart_cache(self) -> None:
        """
        Description / Purpose:
            Loads cart entity records from the repository into the in-memory cache list.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Private helper method called during initialization to populate cart cache.
        """
        for data in self.cart_repo.load_repo():
            self.cart_cache.append(data)

    def _load_order_cache(self) -> None:
        """
        Description / Purpose:
            Loads order receipt records from the order repository into the in-memory cache list.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Private helper method called during initialization to populate order cache.
        """
        for data in self.order_repo.load_repo():
            self.order_cache.append(data)

    def save_order_cache(self) -> None:
        """
        Description / Purpose:
            Persists the in-memory order cache list to storage via the underlying order repository.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Calls order_repo.save_repo() with a snapshot of current order cache contents.
        """
        json_data = [data for data in self.order_cache]
        self.order_repo.save_repo(json_data)

    def process_checkout(self, customer_id: str) -> OrderResponse:
        """
        Description / Purpose:
            Executes full checkout transaction: validates stock, creates OrderItem list, deducts product stock, persists master Order receipt, and clears customer cart.

        Args / Parameters:
            customer_id (str): Unique customer ID string performing checkout.

        Returns:
            OrderResponse: Validated Pydantic OrderResponse schema representing completed receipt.

        Constraints / Notes:
            Raises HTTP 400 Bad Request if cart is empty or if any product lacks sufficient stock.
        """
        customer_cart = [item for item in self.cart_cache if str(item.get('customer_id')) == str(customer_id)]
        if not customer_cart:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot checkout: Your shopping cart is empty."
            )

        products_list = self.product_repo.load_repo()

        # Step 1: Validate stock availability for ALL items before deducting
        for cart_item in customer_cart:
            target_product = next((p for p in products_list if str(p.get('id')) == str(cart_item.get('product_id'))), None)
            if not target_product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product '{cart_item.get('product_name')}' (ID: {cart_item.get('product_id')}) no longer exists."
                )
            if target_product.get('stock_quantity', 0) < cart_item.get('quantity', 0):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for '{target_product.get('product_name')}'. Available: {target_product.get('stock_quantity')}, Requested: {cart_item.get('quantity')}."
                )

        # Step 2: Build OrderItems list and calculate total price
        order_items: list[OrderItem] = []
        total_amount: float = 0.0

        for cart_item in customer_cart:
            target_product = next(p for p in products_list if str(p.get('id')) == str(cart_item.get('product_id')))
            unit_price = float(target_product.get('unit_price', 0.0))
            quantity = int(cart_item.get('quantity', 1))
            line_total = round(quantity * unit_price, 2)

            order_item = OrderItem(
                product_id=str(cart_item.get('product_id')),
                product_name=str(cart_item.get('product_name', target_product.get('product_name'))),
                quantity=quantity,
                unit_price=unit_price,
                total_price=line_total
            )
            order_items.append(order_item)
            total_amount += line_total

            # Step 3: Deduct stock quantity in product inventory
            target_product['stock_quantity'] -= quantity

        # Persist updated stock counts to product.json
        self.product_repo.save_repo(products_list)

        # Step 4: Create master Order record
        new_order = OrderResponse(
            customer_id=str(customer_id),
            order_list=order_items,
            total_amount=round(total_amount, 2)
        )

        self.order_cache.append(new_order.model_dump(mode='json'))
        self.save_order_cache()

        # Step 5: Clear customer's items from cart_cache and save to cart.json
        self.cart_cache = [item for item in self.cart_cache if str(item.get('customer_id')) != str(customer_id)]
        self.save_cart_cache()

        return new_order

    def get_order_history(self, customer_id: str) -> list[dict]:
        """
        Description / Purpose:
            Retrieves all completed past order receipts matching a specific customer ID.

        Args / Parameters:
            customer_id (str): Unique customer ID string.

        Returns:
            list[dict]: List of order receipt dictionaries for the specified customer.

        Constraints / Notes:
            Filters the in-memory order_cache list by customer_id.
        """
        return [order for order in self.order_cache if str(order.get('customer_id')) == str(customer_id)]

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

    def checkout(self, customer_id: str) -> list[OrderItem]:
        order_items = []

        for cart_item in self.cart_cache:
            if cart_item['customer_id'] == customer_id:
                # 1. Look up the product in store inventory to get live price
                product = self.get_product_by_id(cart_item["product_id"], cart_item["merchant_id"])
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product {cart_item['product_id']} no longer exists.")

                unit_price = product["unit_price"]

                # 2. Calculate total price for this line item
                line_total = cart_item["quantity"] * unit_price

                # 3. Build the OrderItem object
                order_item = OrderItem(
                    order_item_id=cart_item["id"],
                    product_id=cart_item["product_id"],
                    product_name=cart_item["product_name"],
                    quantity=cart_item["quantity"],
                    unit_price=unit_price,
                    total_price=line_total
                )
                order_items.append(order_item)

        return order_items

    # [TODO]:
    # - IF THEY HAVE THE SAME PRODUCT ID, CUSTOMER ID, AND MERCHANT ID. ONLY MAKE THE QUANTITY BE CHANGED, DONT ADD ANOTHER RECORD
    # - MAKE SOME RIGHT EXCEPTION HANDLING SO IT HAS BETTER USER EXPERIENCE
    # - REFACTOR

