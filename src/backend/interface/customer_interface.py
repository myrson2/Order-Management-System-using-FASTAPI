import httpx
from backend.schemas.Users import CustomerResponse

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
        response = httpx.get(f'{curr_customer.base_url}/customer/stores/{store_name}/products', timeout=5.0)

        if response.status_code == 200:
            products = response.json()
            print("\n--- AVAILABLE PRODUCTS ---")
            for p in products:
                name = p.get('product_name', 'Unknown')
                price = p.get('unit_price', 0.0)
                stock = p.get('stock_quantity', 0)
                print(f"Product: {name} | Price: ${price:.2f} | Stock: {stock}")
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

def handle_store_shopping(customer: CustomerInterface, store_name: str) -> None:
    """
    Handles the shopping flow inside a specific store:
    - Add To Cart
    - View Cart
    - Edit Order
    - Checkout
    """

    display_store_items(customer, store_name)
    while True:
        store_menu()
        choice = input("Select an option (1-5): ").strip()
        
        match choice:
            case "1":
                print("\n[Action] Add To Cart selected.")
                # TODO: Implement Add to Cart logic
                pass
            case "2":
                print("\n[Action] View Cart selected.")
                # TODO: Implement View Cart logic
                pass
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

def customer_menu() -> None:
    """Displays the main Customer Management Menu."""
    print("\n" + "=" * 40)
    print("        CUSTOMER MANAGEMENT MENU        ")
    print("=" * 40)
    print("1. View/Choose Stores")
    print("2. History")
    print("3. Logout")
    print("=" * 40)

def logout(customer: CustomerInterface) -> bool:
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
        choice = input("Select an option (1-3): ").strip()
        
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
            case "2":
                print("\n[Action] History selected.")
                # TODO: Implement order history retrieval
                pass
            case "3":
                print("\nLogging out...")
                is_logging_out = logout(customer)

                if is_logging_out:
                    break
                else:
                    continue
            case _:
                print("\n[ERROR] Invalid option. Please enter 1-3.")
