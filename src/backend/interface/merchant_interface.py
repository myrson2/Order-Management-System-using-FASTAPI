import httpx

from backend.schemas.Users import MerchantResponse
from backend.schemas.Product import Product
from pydantic import ValidationError


class MerchantInterface:
    """Business logic for managing merchant transactions."""
    def __init__(self, current_merchant: MerchantResponse) -> None:
        """
        Description / Purpose:
            Initializes MerchantInterface with the active merchant's session data
            and constructs the scoped API URL for merchant routes.

        Args / Parameters:
            current_merchant (MerchantResponse): Currently authenticated merchant session object.

        Returns:
            None.

        Constraints / Notes:
            Scopes self.url to http://127.0.0.1:8000/api/v1/merchant/{merchant_id}.
        """
        self.current_merchant = current_merchant
        self.url = f"http://127.0.0.1:8000/api/v1/merchant/{current_merchant.id}"

    def __str__(self) -> str:
        return f"Hello {self.current_merchant.first_name} {self.current_merchant.last_name}"

    def welcome_message(self) -> str:
        """
        Description / Purpose:
            Formats and returns a welcome banner string with merchant name and email.

        Args / Parameters:
            None.

        Returns:
            str: Formatted welcome message string.

        Constraints / Notes:
            Reads directly from self.current_merchant attributes.
        """
        return f"\nLogged in as: {self.current_merchant.first_name} {self.current_merchant.last_name} ({self.current_merchant.email})"

def merchant_menu() -> None:
    """
    Description / Purpose:
        Displays the Merchant Management menu options for product inventory and account settings.

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Prints formatted ASCII options to the terminal console.
    """
    print("\n" + "=" * 40)
    print("        MERCHANT MANAGEMENT MENU        ")
    print("=" * 40)
    print("1. Add Product")
    print("2. Update Stock")
    print("3. Edit Stock")
    print("4. Delete Stock")
    print("5. Settings")
    print("=" * 40)


def settings_menu() -> None:
    """
    Description / Purpose:
        Displays the merchant account settings and session options.

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Prints formatted ASCII menu options to the terminal console.
    """
    print("\n" + "=" * 40)
    print("            SETTINGS MENU               ")
    print("=" * 40)
    print("1. Edit User Profile")
    print("2. Logout")
    print("3. Back to Merchant Menu")
    print("=" * 40)

def edit_profile_flow() -> None:
    """
    Description / Purpose:
        Interactive CLI flow allowing a merchant to update their profile details.

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Feature stub awaiting profile update endpoint wiring.
    """
    pass

def handle_settings(current_merchant: MerchantResponse) -> bool:
    """
    Description / Purpose:
        Controls the interactive settings loop for the merchant, handling profile edits and logout.

    Args / Parameters:
        current_merchant (MerchantResponse): Currently authenticated merchant session.

    Returns:
        bool: True if the merchant logged out successfully, False to return to merchant menu.

    Constraints / Notes:
        Sends HTTP POST to /api/v1/auth/logout via httpx and handles network exceptions.
    """
    while True:
        settings_menu()
        choice = input("Select an option (1-3): ").strip()

        match choice:
            case "1":
                print("\n[Action] Edit User Profile selected.")
                # edit_profile_flow(current_merchant)
            case "2":
                try:
                    response = httpx.post("http://127.0.0.1:8000/api/v1/auth/logout",
                                          json=current_merchant.model_dump(mode='json'))
                    print(f"\n[LOGOUT] Logging out {current_merchant.first_name} {current_merchant.last_name}...")

                    if response.status_code == 200:
                        print(f"\n[LOGOUT] Successfully logged out {current_merchant.first_name} {current_merchant.last_name}.")
                        return True
                    else:
                        print(f"\n[ERROR] Logout failed with status code {response.status_code}: {response.text}")

                except httpx.RequestError as e:
                    print(f"\n[API ERROR] Could not connect to server for logout: {e}")
            case "3":
                print("\nReturning to Merchant Menu...")
                return False
            case _:
                print("\n[ERROR] Invalid option. Please enter 1-3.")

def add_product_flow(merchant: MerchantInterface) -> None:
    """
    Description / Purpose:
        Interactive user input flow to collect product details, validate them
        via the Product schema, and submit to the backend API.

    Args / Parameters:
        merchant (MerchantInterface): The active merchant interface instance containing session and URL.

    Returns:
        None.

    Constraints / Notes:
        Catches ValidationError from Pydantic and RequestError from httpx to prevent CLI crashes.
    """
    print("\n" + "=" * 40)
    print("           ADD NEW PRODUCT              ")
    print("=" * 40)

    try:
        product_name = input("Enter Product Name: ").strip()

        unit_price_raw = input("Enter Unit Price (e.g., 29.99): ").strip()
        try:
            unit_price = float(unit_price_raw)
        except ValueError:
            print("\n[INPUT ERROR] Unit price must be a valid numeric value.")
            return

        stock_quantity_raw = input("Enter Stock Quantity (e.g., 100): ").strip()
        try:
            stock_quantity = int(stock_quantity_raw)
        except ValueError:
            print("\n[INPUT ERROR] Stock quantity must be a valid integer.")
            return

        # Instantiate Product schema to trigger field validators
        product = Product(
            merchant_id=merchant.current_merchant.id,
            product_name=product_name,
            unit_price=unit_price,
            stock_quantity=stock_quantity
        )

        # Submit to merchant's scoped endpoint: POST /api/v1/merchant/{merchant_id}/products
        url = f"{merchant.url}/products"
        response = httpx.post(url, json=product.to_dict(), timeout=5.0)

        if response.status_code in (200, 201):
            print(f"\n[SUCCESS] Product '{product.product_name}' successfully added!")
        else:
            print(f"\n[API ERROR {response.status_code}]: {response.text}")

    except ValidationError as e:
        for err in e.errors():
            field = " -> ".join(str(loc) for loc in err.get("loc", []))
            print(f"\n[VALIDATION ERROR] {field}: {err.get('msg')}")
    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to API server: {e}")


def merchant_interface(current_merchant: MerchantResponse) -> None:
    """
    Description / Purpose:
        Main CLI loop controlling merchant operations including inventory management and settings.

    Args / Parameters:
        current_merchant (MerchantResponse): Currently authenticated merchant session object.

    Returns:
        None.

    Constraints / Notes:
        Exits loop and terminates session when settings logout returns True.
    """
    my_merchant = MerchantInterface(current_merchant)
    print(my_merchant.welcome_message())

    while True:
        merchant_menu()
        choice = input("Select an option (1-5): ").strip()

        match choice:
            case "1":
                add_product_flow(my_merchant)
            case "2":
                print("\n[Action] Update Stock selected.")
                # update_stock_flow()
            case "3":
                print("\n[Action] Edit Stock selected.")
                # edit_stock_flow()
            case "4":
                print("\n[Action] Delete Stock selected.")
                # delete_stock_flow()
            case "5":
                should_logout = handle_settings(current_merchant)
                if should_logout:
                    break
            case _:
                print("\n[ERROR] Invalid option. Please select 1-5.")
