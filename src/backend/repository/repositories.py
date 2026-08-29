import json
from pathlib import Path
from abc import abstractmethod, ABC

class Repository(ABC):
    @abstractmethod
    def save_repo(self, customer_data: list[dict]):
        pass 

    @abstractmethod
    def load_repo(self): 
        pass

class CustomerRepository(Repository):
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
       
    def save_repo(self, customer_data: list[dict]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(customer_data, file, indent=4)
    
    def load_repo(self) -> list[dict]: 
        try: 
            if not self.file_path.exists():
                return []
            with open(self.file_path, "r", encoding="utf-8") as json_file:
                load_file = json.load(json_file)
                return load_file
        except json.JSONDecodeError: 
            return []
    
class OrderRepository(Repository): 
    def __init__(self) -> None: 
        self.order_repos: list[dict] = []
    
    def save_repo(self, order_data: dict):
        self.order_repos.append(order_data)
        return order_data
    
    def load_repo(self) -> list[dict]: 
        return self.order_repos 

