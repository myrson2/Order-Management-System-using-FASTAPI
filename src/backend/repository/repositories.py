import json
from pathlib import Path
from abc import abstractmethod, ABC

class Repository(ABC):
    """Abstract base class defining the repository storage contract."""

    @abstractmethod
    def save_repo(self, data: list[dict]):
        """
        Description / Purpose:
            Abstract method to save a list of data dictionaries to persistent storage.

        Args / Parameters:
            data (list[dict]): List of dictionaries to persist.

        Returns:
            None.

        Constraints / Notes:
            Must be implemented by concrete repository subclasses.
        """
        pass 

    @abstractmethod
    def load_repo(self): 
        """
        Description / Purpose:
            Abstract method to load stored data records from persistent storage.

        Args / Parameters:
            None.

        Returns:
            list[dict]: List of data dictionaries retrieved from storage.

        Constraints / Notes:
            Must be implemented by concrete repository subclasses.
        """
        pass

class CustomerRepository(Repository):
    """Handles persistent reading and writing of customer JSON data."""

    def __init__(self, file_path: Path) -> None:
        """
        Description / Purpose:
            Initializes CustomerRepository with a specific JSON file path.

        Args / Parameters:
            file_path (Path): Path to customer.json storage file.

        Returns:
            None.

        Constraints / Notes:
            Stores the file path reference for load and save operations.
        """
        self.file_path = file_path
       
    def save_repo(self, data: list[dict]) -> None:
        """
        Description / Purpose:
            Writes customer data records into the customer.json file with 4-space indentation.

        Args / Parameters:
            data (list[dict]): List of customer dictionaries to save.

        Returns:
            None.

        Constraints / Notes:
            Creates parent directories automatically if they do not exist.
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    
    def load_repo(self) -> list[dict]: 
        """
        Description / Purpose:
            Reads and parses customer data records from the customer.json file.

        Args / Parameters:
            None.

        Returns:
            list[dict]: List of customer dictionaries (or empty list if file missing/corrupt).

        Constraints / Notes:
            Catches JSONDecodeError and returns an empty list if file is empty or invalid.
        """
        try:
            if not self.file_path.exists():
                return []
            with open(self.file_path, "r", encoding="utf-8") as json_file:
                load_file = json.load(json_file)
                return load_file
        except json.JSONDecodeError: 
            return []

class MerchantRepository(Repository):
    """Handles persistent reading and writing of merchant JSON data."""

    def __init__(self, file_path: Path) -> None:
        """
        Description / Purpose:
            Initializes MerchantRepository with a specific JSON file path.

        Args / Parameters:
            file_path (Path): Path to merchant.json storage file.

        Returns:
            None.

        Constraints / Notes:
            Stores the file path reference for load and save operations.
        """
        self.file_path = file_path

    def save_repo(self, data: list[dict]) -> None:
        """
        Description / Purpose:
            Writes merchant data records into the merchant.json file.

        Args / Parameters:
            data (list[dict]): List of merchant dictionaries to save.

        Returns:
            None.

        Constraints / Notes:
            Creates parent directories automatically if missing.
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_repo(self) -> list[dict]:
        """
        Description / Purpose:
            Reads and parses merchant data records from the merchant.json file.

        Args / Parameters:
            None.

        Returns:
            list[dict]: List of merchant dictionaries (or empty list if file missing/corrupt).

        Constraints / Notes:
            Catches JSONDecodeError and returns an empty list if syntax is invalid.
        """
        try:
            if not self.file_path.exists():
                return []
            with open(self.file_path, "r", encoding="utf-8") as json_file:
                load_file = json.load(json_file)
                return load_file
        except json.JSONDecodeError:
            return []
    
class OrderRepository(Repository): 
    """Handles in-memory storage of order data records."""

    def __init__(self) -> None: 
        """
        Description / Purpose:
            Initializes OrderRepository with an empty in-memory list.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Temporary in-memory storage before database integration.
        """
        self.order_repos: list[dict] = []
    
    def save_repo(self, order_data: dict):
        """
        Description / Purpose:
            Appends an order dictionary record to the in-memory repository list.

        Args / Parameters:
            order_data (dict): Order dictionary payload to save.

        Returns:
            dict: The saved order dictionary.

        Constraints / Notes:
            Appends directly to self.order_repos.
        """
        self.order_repos.append(order_data)
        return order_data
    
    def load_repo(self) -> list[dict]: 
        """
        Description / Purpose:
            Retrieves all order records stored in memory.

        Args / Parameters:
            None.

        Returns:
            list[dict]: List of all order dictionaries.

        Constraints / Notes:
            Returns in-memory list self.order_repos.
        """
        return self.order_repos 

