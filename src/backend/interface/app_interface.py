import os
import httpx
from dotenv import load_dotenv
from backend.interface.handle_user import UserInterface

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
CUSTOMER_URL = f"{API_BASE_URL}/customer"
MERCHANT_URL = f"{API_BASE_URL}/merchant"
ORDER_URL = f"{API_BASE_URL}/order"
user_interface = UserInterface(CUSTOMER_URL, MERCHANT_URL)

def menu() -> None: 
    """
    Description / Purpose:
        Displays the main unauthenticated terminal menu options (Login, Register, Exit).

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Prints formatted ASCII menu to terminal.
    """
    print("\n" + "=" * 40)
    print("   ORDER MANAGEMENT SYSTEM (API BASED SYSTEM)")
    print("=" * 40)

    print("1. Login")
    print("2. Register New Account")
    print("3. Exit")
    print("=" * 40)

def order_menu() -> None:
    """
    Description / Purpose:
        Displays the logged-in user menu options (Open Customer Menu, Edit Account, Logout).

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Only presented when current_user session is active.
    """
    print("1. Open Customer Management Menu")
    print("2. Edit Account")
    print("3. Logout")
    print("=" * 40)

def main_interface() -> None:
    """
    Description / Purpose:
        Main CLI loop controlling state transitions between logged-out and logged-in user sessions.

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Runs infinite loop until user selects exit choice (3). Communicates with FastAPI via httpx.
    """
    current_user = None  # Holds logged-in customer session data

    while True:
        # STATE 1: NOT LOGGED IN
        if current_user is None:
            menu()
            choice = input("Select option (1-3): ").strip()

            match choice:
                case "1": # Login 
                    current_user = user_interface.user_authentication()
                    if current_user is not None: 
                        print(f"\nLogged in as: {current_user.first_name} {current_user.last_name} ({current_user.email})")
                case "2": # Register 
                    user_interface.account_registration()
                case "3":
                    print("\nExiting System. Goodbye!")
                    break
                case _:
                    print("\n[ERROR] Invalid choice. Enter 1-3.")
        else:

            if current_user is None:
                return
            #Order Interface
            order_menu()
            choice = input("Select option (1-3): ").strip()

            match choice:
                case "1":
                    pass
                case "2":
                    # print(current_user.id)
                    # print("\nPress Enter to skip entries you don't want to edit.")
                    # first_name = input("First Name: ").strip()
                    # last_name = input("Last Name: ").strip()
                    # email = input("Email: ").strip()
                    # phone_num = input("Phone Number: ").strip()
                    #
                    # data = CustomerUpdate(
                    #     first_name=first_name if first_name else None,
                    #     last_name=last_name if last_name else None,
                    #     email=email if email else None,
                    #     phone=phone_num if phone_num else None,
                    # )
                    #
                    # response = httpx.patch(
                    #     f"{CUSTOMER_URL}/{current_user.id}",
                    #     json=data.model_dump(mode='json', exclude_none=True),
                    #     timeout=5.0
                    # )
                    #
                    # if response.status_code == 200:
                    #     print(f"\n[API 200 SUCCESS] Account updated successfully!")
                    # else:
                    #     print(f"\n[API ERROR {response.status_code}]: {response.text}")
                    pass
                case "3":
                    print(f"\n[SUCCESS] Logged out {current_user.first_name}.")
                    current_user = None  # Reset session state
                case _:
                    print("\n[ERROR] Invalid choice. Enter 1-3.")

if __name__ == "__main__":
    main_interface()