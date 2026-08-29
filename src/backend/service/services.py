from backend.repository.repositories import CustomerRepository
from backend.schemas.Customer import Customer

class CustomerService: 
    def __init__(self, customer_repo: CustomerRepository) -> None: 
        self.customer_repo = customer_repo
        self.customer_cache: list[dict] = []
        self._load_customer_cache()

    def _load_customer_cache(self) -> None: 
        for customer_data in self.customer_repo.load_repo():
            self.customer_cache.append(customer_data)

    def save_customer_cache(self) -> None:
        json_data = [customer for customer in self.customer_cache]
        self.customer_repo.save_repo(json_data)

    def get_customers(self) -> list[dict]:
        return self.customer_cache

    def add_customer(self, customer_data: dict) -> None:
        self.customer_cache.append(customer_data)
        self.save_customer_cache()

    def get_customer_by_id(self, customer_id: int) -> dict | None:
        customers = self.get_customers()
        for c in customers:
            if c.get("customer_id") == customer_id:
                return c
        return None

class OrderService:
    def __init__(self, order_repo) -> None:
        self.order_repo = order_repo