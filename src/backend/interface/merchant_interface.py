import httpx
from backend.schemas.Users import MerchantResponse
from backend.schemas.Product import ProductCreate, ProductResponse, ProductUpdate
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
        self.base_url = "http://127.0.0.1:8001/api/v1/merchant"
        self.url = f"http://127.0.0.1:8001/api/v1/merchant/{current_merchant.id}"

    def __str__(self) -> str:
        """
        Description / Purpose:
            Returns a friendly informal greeting string identifying the merchant by full name.

        Args / Parameters:
            None.

        Returns:
            str: Greeting string including merchant's first and last name.

        Constraints / Notes:
            Reads attributes directly from self.current_merchant.
        """
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

def update_stock_menu() -> None:
    """
    Description / Purpose:
        Displays the stock management submenu options (Deduct Stock, Restock).

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Prints formatted ASCII menu options to the terminal console.
    """
    print("\n" + "=" * 40)
    print("          UPDATE STOCK MENU             ")
    print("=" * 40)
    print("1. Deduct Stock")
    print("2. Restock")
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
                    response = httpx.post("http://127.0.0.1:8001/api/v1/auth/logout",
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
        product = ProductCreate(
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

def display_all_products(merchant: MerchantInterface) -> list[dict]:
    """
    Description / Purpose:
        Fetches the complete catalog of products from the backend API.

    Args / Parameters:
        merchant (MerchantInterface): The active merchant interface instance containing base URL info.

    Returns:
        list[dict]: List of product dictionaries retrieved from the API, or empty list on network error.

    Constraints / Notes:
        Handles httpx.RequestError gracefully if backend connection fails.
    """
    try:
        response = httpx.get(f"{merchant.base_url}/products", timeout=5.0)
        if response.status_code == 200:
            return response.json()
        print(f"\n[API ERROR {response.status_code}]: {response.text}")
        return []
    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to API server: {e}")
        return []

def delete_stock_flow(product_id: str, merchant: MerchantInterface) -> None:
    """
    Description / Purpose:
        Sends an HTTP DELETE request to remove a specific product from the merchant's catalog.

    Args / Parameters:
        product_id (str): The unique identifier of the product to delete.
        merchant (MerchantInterface): The active merchant interface containing session and URL configurations.
        all_products (list | None): Optional cached list of current products.

    Returns:
        None.

    Constraints / Notes:
        Handles httpx.RequestError for network failures and checks HTTP status codes
        (200/204 for success, 404 for missing items, and other unexpected status codes).
    """
    try:
        response = httpx.delete(f"{merchant.url}/products/{product_id}", timeout=5.0)

        if response.status_code == 200:
            # 1. Parse the JSON body from the HTTP response
            payload = response.json()

            # 2. Feed it into your Pydantic schema!
            deleted_product = ProductResponse(**payload)

            # 3. Now you have full access to typed attributes!
            print(f"\n[SUCCESS] Product '{deleted_product.product_name}' (ID: {product_id}) was successfully deleted.")

        elif response.status_code == 404:
            print(f"\n[NOT FOUND] No product matches ID '{product_id}'. Please verify the ID and try again.")
        else:
            print(f"\n[API ERROR {response.status_code}]: {response.text}")

    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to API server: {e}")


def restock_flow(merchant: MerchantInterface, additions: int, product_data: ProductResponse) -> None:
    """
    Description / Purpose:
        Computes updated stock level, validates via ProductUpdate schema, and transmits
        a PATCH request to restock the target product on the backend API.

    Args / Parameters:
        merchant (MerchantInterface): The active merchant session containing URL configurations.
        additions (int): Quantity of items to add to current inventory stock.
        product_data (ProductResponse): The current product schema model instance.

    Returns:
        None.

    Constraints / Notes:
        Validates additions > 0 and sends exclude_unset=True payload via httpx.patch.
    """
    try:
        amount = int(additions)
        if amount <= 0:
            print("\n[INPUT ERROR] Restock amount must be greater than zero.")
            return
    except ValueError:
        print("\n[INPUT ERROR] Please enter a valid whole number.")
        return

    # 2. Perform calculation
    added_stock = product_data.stock_quantity + amount

    # 3. Create update schema & exclude unset fields
    update_data = ProductUpdate(stock_quantity=added_stock)
    payload = update_data.model_dump(exclude_unset=True)  # Produces: {"stock_quantity": new_stock}

    # 4. Send HTTP request to backend
    try:
        url = f"{merchant.url}/products/{product_data.id}/restock"
        response = httpx.patch(url, json=payload, timeout=5.0)

        if response.status_code == 200:
            # 5. Update local object so the menu shows the new stock immediately!
            product_data.stock_quantity = added_stock
            print(f"\n[SUCCESS] Successfully restocked '{product_data.product_name}'!")
            print(f"New Stock Level: {product_data.stock_quantity}")
        else:
            print(f"\n[API ERROR {response.status_code}]: {response.text}")

    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to API server: {e}")

def deduct_stock_flow(merchant: MerchantInterface, deductions: int, product_data: ProductResponse) -> None:
    """
    Description / Purpose:
        Handles interactive inventory deduction workflow for subtracting units from stock.

    Args / Parameters:
        merchant (MerchantInterface): Active merchant session with API routing context.
        deductions (int): Quantity of units to subtract from stock.
        product_data (ProductResponse): Current product schema representation.

    Returns:
        None.

    Constraints / Notes:
        Feature stub awaiting backend deduction endpoint wiring.
    """
    try:
        amount = int(deductions)
        if amount <= 0:
            print("\n[INPUT ERROR] Restock amount must be greater than zero.")
            return
    except ValueError:
        print("\n[INPUT ERROR] Please enter a valid whole number.")
        return

    # 2. Perform calculation
    deducted_stock = product_data.stock_quantity - amount

    # 3. Create update schema & exclude unset fields
    update_data = ProductUpdate(stock_quantity=deducted_stock)
    payload = update_data.model_dump(exclude_unset=True)  # Produces: {"stock_quantity": new_stock}

    # 4. Send HTTP request to backend
    try:
        url = f"{merchant.url}/products/{product_data.id}/deduct"
        response = httpx.patch(url, json=payload, timeout=5.0)

        if response.status_code == 200:
            # 5. Update local object so the menu shows the new stock immediately!
            product_data.stock_quantity = deducted_stock
            print(f"\n[SUCCESS] Successfully deducted '{product_data.product_name}'!")
            print(f"New Stock Level: {product_data.stock_quantity}")
        else:
            print(f"\n[API ERROR {response.status_code}]: {response.text}")

    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to API server: {e}")

def update_stock_flow(merchant: MerchantInterface, product_data: ProductResponse) -> None:
    """
    Description / Purpose:
        Controls the interactive stock adjustment loop for deducting or replenishing inventory.

    Args / Parameters:
        merchant (MerchantInterface): The active merchant interface session object.

    Returns:
        None.

    Constraints / Notes:
        Loops until the merchant selects the option to return to the main menu.
    """
    while True:
        print(f"Product: {product_data.product_name}")
        update_stock_menu()
        choice = input("Select an option (1-3): ").strip()

        match choice:
            case "1":
                print("\n[Action] Deduct Stock selected.")
                deductions = int(input("Deductions: "))
                deduct_stock_flow(merchant, deductions, product_data)
            case "2":
                print("\n[Action] Restock selected.")
                additions = int(input("Additions: "))
                restock_flow(merchant, additions, product_data)
            case "3":
                print("\nReturning to Merchant Menu...")
                break
            case _:
                print("\n[ERROR] Invalid option. Please select 1-3.")


def edit_stock_flow(my_merchant: MerchantInterface, product_data: ProductResponse) -> None:
    """
    Description / Purpose:
        Prompts merchant to edit the product name and unit price (excluding stock quantity),
        validates the inputs via ProductUpdate schema, and sends a PATCH request to the backend.

    Args / Parameters:
        my_merchant (MerchantInterface): Active merchant session with scoped URL configurations.
        product_data (ProductResponse): The target product schema instance to be edited.

    Returns:
        None.

    Constraints / Notes:
        Validates unit price is positive (> 0).
        Transmits only product_name and unit_price using exclude_unset=True.
    """
    print("\n" + "=" * 40)
    print(f"        EDIT PRODUCT: {product_data.product_name}")
    print("=" * 40)

    # 1. User Input for Product Name
    raw_name = input(f"Enter New Product Name (Press Enter to keep '{product_data.product_name}'): ").strip()
    new_name = raw_name if raw_name else product_data.product_name

    # 2. User Input for Unit Price
    raw_price = input(f"Enter New Unit Price (Press Enter to keep {product_data.unit_price}): ").strip()
    if raw_price:
        try:
            new_price = float(raw_price)
            if new_price <= 0:
                print("\n[INPUT ERROR] Unit price must be greater than zero.")
                return
        except ValueError:
            print("\n[INPUT ERROR] Please enter a valid number for unit price.")
            return
    else:
        new_price = product_data.unit_price

    # 3. Create update schema with name and unitprice only (stock_quantity excluded)
    update_data = ProductUpdate(
        product_name=new_name,
        unit_price=new_price
    )
    payload = update_data.model_dump(exclude_unset=True)

    # 4. Transmit PATCH request to backend
    try:
        url = f"{my_merchant.url}/products/{product_data.id}/edit"
        response = httpx.patch(url, json=payload, timeout=5.0)

        if response.status_code == 200:
            product_data.product_name = new_name
            product_data.unit_price = new_price
            print(f"\n[SUCCESS] Product successfully updated!")
            print(f"Name: {product_data.product_name} | Price: {product_data.unit_price:.2f} | Stock: {product_data.stock_quantity}")
        else:
            print(f"\n[API ERROR {response.status_code}]: {response.text}")

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
                try:
                    all_products = display_all_products(my_merchant)
                    if not all_products:
                        continue

                    print(all_products)
                    select_product = input("Enter Product ID: ").strip()

                    response = httpx.get(f"{my_merchant.url}/products/{select_product}", timeout=5.0)

                    if response.status_code == 200:
                       payload = response.json()
                       update_stock_flow(my_merchant, ProductResponse(**payload))
                    elif response.status_code == 404:
                        error_detail = response.json().get("detail", "Product not found.")
                        print(f"\n[NOT FOUND] {error_detail}")

                except httpx.RequestError as e:
                   print(f"\n[ERROR] Could not connect to API server: {e}")
            case "3":
                print("\n[Action] Edit Stock selected.")
                all_products = display_all_products(my_merchant)
                print(all_products)

                edit_product_id = input("Enter Product ID: ").strip()
                response = httpx.get(f"{my_merchant.url}/products/{edit_product_id}", timeout=5.0)

                if response.status_code == 200:
                    payload = response.json()
                    edit_stock_flow(my_merchant, ProductResponse(**payload))
                elif response.status_code == 404:
                    error_detail = response.json().get("detail", "Product not found.")
                    print(f"\n[NOT FOUND] {error_detail}")
            case "4":
                print("\n[Action] Delete Stock selected.")
                all_products = display_all_products(my_merchant)
                print(all_products)
                delete_product_id = input("Enter Product ID: ").strip()
                delete_stock_flow(delete_product_id, my_merchant)
            case "5":
                should_logout = handle_settings(current_merchant)
                if should_logout:
                    break
            case _:
                print("\n[ERROR] Invalid option. Please select 1-5.")
