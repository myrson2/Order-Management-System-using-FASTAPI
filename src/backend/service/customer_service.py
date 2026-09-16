import httpx

from backend.service.user_service import UserService

class CustomerService(UserService):
    """Business logic and caching service for customer operations."""
    def __init__(self, repositories):
        super().__init__(repositories)


