import httpx

from backend.schemas.Cart import CartCreate, CartResponse
from backend.schemas.OrderItems import OrderItem, OrderItemCreate
from backend.schemas.Users import CustomerResponse, MerchantResponse


class CustomerInterface:
    """CLI client interface handler for Customer operations."""
    
    def __init__(self, current_customer: CustomerResponse):
        """
        Initializes CustomerInterface with active session data and base URL.
        Sets up an empty in-memory cart.
        """
        self.current_customer = current_customer
        self.base_url = "http://127.0.0.1:8001/api/v1"
        self.customer_url = f"{self.base_url}/customer/{current_customer.id}"

    def welcome_message(self) -> str:
        """Returns a formatted welcome string."""
        return f"\nLogged in as: {self.current_customer.first_name} {self.current_customer.last_name} ({self.current_customer.email}) | Rewards: ${self.current_customer.rewards:.2f}"

def display_stores(curr_customer: CustomerInterface) -> list[dict]:
    """Fetches and displays all registered merchants (stores)."""
    try:
        response = httpx.get(f'{curr_customer.base_url}/customer/stores', timeout=5.0)
        if response.status_code == 200:
            print(response)
            return response.json()
        else :
            print(response)
            return []
    except httpx.RequestError as e:
        print(f"\n[API ERROR] Network failed: {e}")
        return []

def display_store_items(curr_customer: CustomerInterface, store_name: str) -> None:
    """Fetches and displays available products for a specific merchant."""
    try:
        response = httpx.get(f'{curr_customer.base_url}/customer/stores/{store_name}/all_products', timeout=5.0)

        if response.status_code == 200:
            products = response.json()
            print("\n--- AVAILABLE PRODUCTS ---")
            for p in products:
                name = p.get('product_name', 'Unknown')
                price = p.get('unit_price', 0.0)
                stock = p.get('stock_quantity', 0)
                id = p.get('id')
                print(f"Product_ID: {id} | Product: {name} | Price: ${price:.2f} | Stock: {stock}")
            print("--------------------------\n")
        else:
            print('Doesnt Have Products')
    except httpx.RequestError as e:
        print(f"\n[API ERROR] Network failed: {e}")

def store_menu() -> None:
    """Displays the interactive menu inside a store."""
    print("\n" + "=" * 40)
    print("             STORE MENU                 ")
    print("=" * 40)
    print("1. Add To Cart")
    print("2. View Cart")
    print("3. Edit Order (Cart)")
    print("4. Checkout")
    print("5. Exit Store")
    print("=" * 40)

def add_to_cart(customer: CustomerInterface, merchant: MerchantResponse) -> CartResponse | None:
    """
    Description / Purpose:
        CLI interactive prompt collecting Product ID and quantity to submit a new cart item to the backend API.

    Args / Parameters:
        customer (CustomerInterface): Active customer session interface instance.
        merchant (MerchantResponse): MerchantResponse schema instance representing the selected store.

    Returns:
        CartResponse | None: CartResponse object upon successful API creation, or None on failure.

    Constraints / Notes:
        Sends HTTP POST request to /cart/customer/{customer_id}/add using httpx.
    """
    try:
        #make validation for prd_id if that id is there or not
        prd_id = input("\nEnter Product ID: ")
        qty = int(input("\nEnter Quantity: "))

        prd_items = CartCreate(
            customer_id=str(customer.current_customer.id),
            merchant_id=str(merchant.id),
            product_id=prd_id,
            quantity=qty
        )

        add_to_cart_response = httpx.post(
            f'{customer.base_url}/cart/customer/{customer.current_customer.id}/add',
            json=prd_items.model_dump(mode='json')
        )

        if add_to_cart_response.status_code == 201:
            print(f'Customer Added An Item Successfully.')
            return CartResponse(**add_to_cart_response.json())
        else:
            print(f"[API ERROR {add_to_cart_response.status_code}]: {add_to_cart_response.text}")
    except httpx.RequestError as e:
        print(f"\n[API ERROR] Network failed: {e}")

def view_cart(customer: CustomerInterface) -> None:
    """
    Description / Purpose:
        Fetches and displays active cart items for the logged-in customer from the backend API.

    Args / Parameters:
        customer (CustomerInterface): Active customer session interface instance.

    Returns:
        None.

    Constraints / Notes:
        Sends HTTP GET request to /cart/customer/{customer_id}/view and formats output to terminal.
    """
    response = httpx.get(f'{customer.base_url}/cart/customer/{customer.current_customer.id}/view')
    if response.status_code == 200:
        cart_items = response.json()
        if not cart_items:
            print("\n[INFO] Your shopping cart is empty.")
        else:
            print("\n--- YOUR CART ---")
            for item in cart_items:
                print(f"Product ID: {item.get('product_id')} | Quantity: {item.get('quantity')}")
            print("-----------------\n")
    else:
        print(f"\n[ERROR {response.status_code}]: {response.text}")

def handle_store_shopping(customer: CustomerInterface, store_name: str) -> None:
    """
    Handles the shopping flow inside a specific store:
    - Add To Cart
    - View Cart
    - Edit Order
    - Checkout
    """

    # Get merchant object using store name
    try:
        merchant = httpx.get(f'{customer.base_url}/customer/stores/{store_name}')
        merchant_res = MerchantResponse(**merchant.json())
        if merchant.status_code == 200:
            display_store_items(customer, store_name)  # Change Store name to Merchant Object
            while True:
                store_menu()
                choice = input("Select an option (1-5): ").strip()

                match choice:
                    case "1":
                        print("\n[Action] Add To Cart selected.")
                        add_to_cart(customer, merchant_res)
                    case "2":
                        print("\n[Action] View Cart selected.")
                        view_cart(customer)
                    case "3":
                        print("\n[Action] Edit Order selected.")
                        # TODO: Implement Edit Order logic
                        pass
                    case "4":
                        print("\n[Action] Checkout selected.")
                        # TODO: Implement Checkout logic
                        pass
                    case "5":
                        print("\nReturning to Customer Management Menu...")
                        break
                    case _:
                        print("\n[ERROR] Invalid option. Please enter 1-5.")
        else:
            return None
    except httpx.RequestError as e:
        print(e)

def customer_menu() -> None:
    """Displays the main Customer Management Menu."""
    print("\n" + "=" * 40)
    print("        CUSTOMER MANAGEMENT MENU        ")
    print("=" * 40)
    print("1. View/Choose Stores")
    print('2. View Cart')
    print("3. History")
    print("4. Logout")
    print("=" * 40)

def logout(customer: CustomerInterface) -> bool:
    """
    Description / Purpose:
        Sends an HTTP POST request to terminate the active customer authentication session.

    Args / Parameters:
        customer (CustomerInterface): Active customer session interface instance.

    Returns:
        bool: True if logout succeeds (HTTP 200), False otherwise.

    Constraints / Notes:
        Sends customer profile payload to /auth/logout endpoint.
    """
    try:
        response = httpx.post("http://127.0.0.1:8001/api/v1/auth/logout",
                              json=customer.current_customer.model_dump(mode='json'))
        print(f"\n[LOGOUT] Logging out {customer.current_customer.first_name} {customer.current_customer.last_name}...")

        if response.status_code == 200:
            print(
                f"\n[LOGOUT] Successfully logged out {customer.current_customer.first_name} {customer.current_customer.last_name}.")
            return True
        else:
            print(f"\n[ERROR] Logout failed with status code {response.status_code}: {response.text}")
            return False

    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to server for logout: {e}")
        return False

def customer_interface(current_customer: CustomerResponse) -> None:
    """
    Main CLI loop for the Customer.
    Handles:
    - View/Choose Stores
    - History
    - Logout
    """
    customer = CustomerInterface(current_customer)
    print(customer.welcome_message())
    
    while True:
        customer_menu()
        choice = input("Select an option (1-4): ").strip()
        
        match choice:
            case "1":
                print("\n[Action] View/Choose Stores selected.")
                stores = display_stores(customer)

                if stores is None or len(stores) == 0:
                    print('Dont have any stores available.')
                else:
                    for store in stores:
                        print(f"Store ID: {store.get('id')} | Name: {store.get('store_name')}")

                merchant_store = input("Enter store name: ")

                if any(str(store.get("store_name")) == merchant_store for store in stores):
                    handle_store_shopping(customer, merchant_store)
                else:
                    print("Invalid store name.")
            case '2':
                print("\n[Action] View Cart")
                view_cart(customer)

            case "3":
                print("\n[Action] History selected.")
                # TODO: Implement order history retrieval
                pass
            case "4":
                print("\nLogging out...")
                is_logging_out = logout(customer)

                if is_logging_out:
                    break
                else:
                    continue
            case _:
                print("\n[ERROR] Invalid option. Please enter 1-4.")
