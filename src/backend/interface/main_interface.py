import os
import httpx
from dotenv import load_dotenv
from backend.schemas.Customer import Customer
from pydantic import ValidationError

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
CUSTOMER_URL = f"{API_BASE_URL}/customer"

def menu(): 
    print("\n" + "=" * 40)
    print("   ORDER MANAGEMENT SYSTEM (API BASED SYSTEM)")
    print("=" * 40)

    print("1. Login")
    print("2. Register New Account")
    print("3. Exit")
    print("=" * 40)

def user_authentication() -> Customer | None: 
    print("\n--- LOGIN ---")

    try:
        email = input("Enter Email (Format: @gmail.com): ").strip()    
        password = input("Enter Password: ").strip()
    
        # Query API Controller for customers list
        response = httpx.get(f"{CUSTOMER_URL}/", timeout=5.0)

        if response.status_code == 200:
            customers = response.json()
            user_match = next(
                (c for c in customers if c.get("email") == email and c.get("password") == password),
                None
            )
            if user_match is None:
                print("\n[LOGIN FAILED] Invalid email or password.")
                return None
            
            print(f"\nWelcome back, {user_match.get('first_name')} {user_match.get('last_name')}!")
            return Customer.from_dict(user_match)

        else:
            raise ConnectionError(f"\n[ERROR {response.status_code}]: {response.text}")
    
    except ValueError as e:
        print(f"\n{e}")
        return None
    except httpx.RequestError: 
        print("\n[API ERROR] Could not connect to server. Ensure FastAPI is running on http://127.0.0.1:8000")
        return None

def account_registration(): 
    print("\n--- REGISTER NEW ACCOUNT ---")
    try:
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        email = input("Email: ").strip()
        phone_num = input("Phone Number: ").strip()
        pwd = input("Password (min 8 chars): ").strip()

        payload = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone_num,
            password=pwd
        )
        # Send HTTP POST to API Controller
        response = httpx.post(f"{CUSTOMER_URL}/", json=payload.to_dict(), timeout=5.0)
        if response.status_code == 201:
            print(f"\n[API 201 SUCCESS] Account registered! You can now log in.")
        else:
            print(f"\n[API ERROR {response.status_code}]: {response.text}")
    except ValidationError as e:
        print(f"\n[ERROR] {e}")
    except httpx.ConnectError:
        print("\n[API ERROR] Could not connect to API server.")


def main_interface():
    """
    Main CLI Interface using HTTP API Client requests via httpx.
    Communicates directly with FastAPI Controller endpoints.
    """
    current_user = None  # Holds logged-in customer session data

    while True:
        # STATE 1: NOT LOGGED IN
        if current_user is None:
            menu()
            choice = input("Select option (1-3): ").strip()

            match choice:
                case "1": # Login 
                    current_user = user_authentication()
                    if current_user is not None: 
                        print(f"\n[API 200 SUCCESS] Welcome!! {current_user.first_name} {current_user.last_name}!")
                case "2": # Register 
                    account_registration()
                case "3":
                    print("\nExiting System. Goodbye!")
                    break
                case _:
                    print("\n[ERROR] Invalid choice. Enter 1-3.")
        else:
            print(f"\nLogged in as: {current_user.get('first_name')} {current_user.get('last_name')} ({current_user.get('email')})")
            print("1. Open Customer Management Menu")
            print("2. Logout")
            print("3. Exit")
            print("=" * 40)

            choice = input("Select option (1-3): ").strip()

            if choice == "1":
                # customer_interface()
                pass
            elif choice == "2":
                print(f"\n[SUCCESS] Logged out {current_user.get('first_name')}.")
                current_user = None  # Reset session state
            elif choice == "3":
                print("\nExiting System. Goodbye!")
                break
            else:
                print("\n[ERROR] Invalid choice. Enter 1-3.")

if __name__ == "__main__":
    main_interface()