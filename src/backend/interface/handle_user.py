import httpx

from backend.schemas.Users import Customer, Merchant
from backend.schemas.Users.User import User, UserCreate
from pydantic import ValidationError
from backend.schemas.Users.User import EnumType

class UserInterface:
    """CLI client interface handler for user authentication and account registration."""

    def __init__(self, customer_url: str, merchant_url: str):
        """
        Description / Purpose:
            Initializes UserInterface with target API endpoints for customer and merchant operations.

        Args / Parameters:
            customer_url (str): API endpoint URL for customer routes.
            merchant_url (str): API endpoint URL for merchant routes.

        Returns:
            None.

        Constraints / Notes:
            Stores URLs for HTTP client requests via httpx.
        """
        self.customer_url = customer_url
        self.merchant_url = merchant_url

    def user_authentication(self) -> User | None:
        """
        Description / Purpose:
            Prompts for credentials, queries API controller over HTTP, and verifies user login.

        Args / Parameters:
            None.

        Returns:
            User | None: Logged-in Customer/User object if authentication succeeds, or None.

        Constraints / Notes:
            Sends HTTP GET request to API backend and handles network/validation exceptions.
        """
        print("\n--- LOGIN ---")

        try:
            email = input("Enter Email (Format: @gmail.com): ").strip()
            password = input("Enter Password: ").strip()

            # Query API Controller for customers list
            response = httpx.get(f"{self.customer_url}/", timeout=5.0)

            if response.status_code == 200:
                customers = response.json()
                user_match = next(
                    (c for c in customers if c.get("email") == email and c.get("password") == password),
                    None
                )
                if user_match is None:
                    print("\n[LOGIN FAILED] Invalid email or password.")
                    return None
                return Customer.from_dict(user_match)

            else:
                raise ConnectionError(f"\n[ERROR {response.status_code}]: {response.text}")

        except ValueError as e:
            print(f"\n{e}")
            return None
        except httpx.RequestError:
            print("\n[API ERROR] Could not connect to server. Ensure FastAPI is running on http://127.0.0.1:8000")
            return None

    def account_registration(self):
        """
        Description / Purpose:
            Interactive CLI registration prompt collecting user details and submitting payloads to API backend.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Supports customer and merchant account types. Sends HTTP POST request over network via httpx.
        """
        print("\n--- REGISTER NEW ACCOUNT ---")
        data = None
        response = None

        try:
            loop = True
            while loop:
                try:
                    first_name = input("First Name: ").strip()
                    last_name = input("Last Name: ").strip()
                    email = input("Email: ").strip()
                    phone_num = input("Phone Number: ").strip()
                    pwd = input("Password (min 8 chars): ").strip()
                    u_type = input("User Type: (Customer/Merchant)").strip().lower()

                    match u_type:
                        case "merchant":
                            merchant_store_name = input("Merchant Store Name: ").strip()

                            data = Merchant(
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                phone=phone_num,
                                password=pwd,
                                store_name=merchant_store_name
                            )
                            response = httpx.post(f"{self.merchant_url}/", json=data.to_dict(), timeout=5.0)
                        case "customer":
                            data = Customer(
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                phone=phone_num,
                                password=pwd
                            )
                            response = httpx.post(f"{self.customer_url}/", json=data.to_dict(), timeout=5.0)
                        case _:
                            raise ValueError(f"\n[ERROR]: User type ({u_type}) is not valid.")

                    loop = False

                except ValidationError as e:
                    print(e)
                except ValueError as e:
                    print(e)

            if data is None:
                raise ValueError("\n[ERROR] No data provided.")

            # Send HTTP POST to API Controller

            if response.status_code == 201:
                print(f"\n[API 201 SUCCESS] Account registered! You can now log in.")
            else:
                print(f"\n[API ERROR {response.status_code}]: {response.text}")
        except ValidationError as e:
            print(f"\n[ERROR] {e}")
        except httpx.ConnectError:
            print("\n[API ERROR] Could not connect to API server.")