class OrderService:
    """Business logic service for managing order transactions."""

    def __init__(self, order_repo) -> None:
        """
        Description / Purpose:
            Initializes OrderService with an OrderRepository dependency.

        Args / Parameters:
            order_repo: Order data access repository instance.

        Returns:
            None.

        Constraints / Notes:
            Stores repository reference for order operations.
        """
        self.order_repo = order_repo