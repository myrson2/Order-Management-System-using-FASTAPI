# 🌐 Comprehensive Guide to FastAPI API Integration

This guide provides a thorough explanation of how the **HTTP API Integration** approach is structured in this project, explaining how the terminal CLI interface communicates with the FastAPI controller endpoints over the network.

---

## 🎯 High-Level Architectural Concept

In a modern web application, backend services are decoupled from frontend clients using **Client-Server Architecture**:

```text
┌──────────────────────────────────────┐             ┌──────────────────────────────────────┐
│           CLIENT LAYER               │             │            BACKEND SERVER            │
│  (CLI Menu / React / Mobile App)     │             │            (FastAPI App)             │
│                                      │   HTTP POST │                                      │
│   user_interface.py / main_interface  │────────────►│  app.py (Listens on port 8000)       │
│   (Sends JSON over network via httpx)│             │          │                           │
│                                      │  HTTP JSON  │          ▼                           │
│                                      │◄────────────│  CustomerController.py               │
│                                      │  Response   │          │                           │
└──────────────────────────────────────┘             │          ▼                           │
                                                     │  CustomerService / Repository        │
                                                     └──────────────────────────────────────┘
```

### Key Takeaway: Network Decoupling
- The **CLI Interface** (`user_interface.py` / `main_interface.py`) does **NOT** import `CustomerController.py` or call backend Python functions directly.
- Instead, the CLI acts as an **independent HTTP Client** (using `httpx`) that sends network requests to `http://127.0.0.1:8000/api/v1/customer`.
- The **FastAPI Server** (`app.py`) listens on port 8000, inspects incoming URL paths, and routes requests to the corresponding controller functions.

---

## 🔁 Step-by-Step Data Flow

When a user interacts with the system (e.g. adding a customer):

```text
[User Terminal Input]
        │
        ▼
[1] main_interface.py / user_interface.py
    └── Collects input (ID, Name, Email, Phone, Password)
    └── Packs input into a Python dictionary: payload = {...}
    └── Calls: httpx.post("http://127.0.0.1:8000/api/v1/customer/", json=payload)
        │
        ▼  (HTTP POST Network Request)
[2] FastAPI Uvicorn Web Server (Port 8000)
    └── Listens on http://127.0.0.1:8000
    └── Matches request path `/api/v1/customer/` against registered APIRouter prefix
        │
        ▼  (Routes request to handler)
[3] CustomerController.py
    └── @router.post("/", status_code=201)
    └── Validates payload using Pydantic Customer model
    └── Calls service.add_customer(customer.to_dict())
        │
        ▼
[4] CustomerService & CustomerRepository
    └── Saves customer data to in-memory repository
        │
        ▼  (HTTP 201 Created Response)
[5] httpx Client in CLI Interface
    └── Receives response.status_code == 201
    └── Prints: [API 201 SUCCESS] Customer 'John Doe' created!
```

---

## 🧩 Deep Dive: Code Breakdown Across Layers

### 1. The Controller Layer ([`CustomerController.py`](file:///c:/Users/JoseMyrsonOBeros/Documents/Python/Mini%20Projects/Order%20Management%20System/backend/src/backend/controller/CustomerController.py))

```python
from fastapi import APIRouter, Depends, HTTPException, status
from backend.repository.repositories import CustomerRepository
from backend.service.services import CustomerService
from backend.schemas.Customer import Customer

customer_repository = CustomerRepository()


def get_customer_service() -> CustomerService:
    return CustomerService(customer_repository)


# 1. Define path prefix for all customer routes
router = APIRouter(prefix="/api/v1/customer", tags=["Customer"])


# 2. GET Endpoint: Returns all customers
@router.get("/")
def get_customers(service: CustomerService = Depends(get_customer_service)):
    return service.get_customers()


# 3. GET by ID Endpoint: Returns customer by ID or 404
@router.get("/{customer_id}")
def get_customer_by_id(customer_id: int, service: CustomerService = Depends(get_customer_service)):
    customer = service.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


# 4. POST Endpoint: Creates customer validated via Pydantic Customer model
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_customer(customer: Customer, service: CustomerService = Depends(get_customer_service)):
    return service.add_customer(customer.to_dict())
```

#### Why `APIRouter(prefix="/api/v1/customer")`?
- Setting `prefix="/api/v1/customer"` groups all related endpoints under a clean namespace URL.
- When `@router.get("/")` is defined, the full request path becomes `http://127.0.0.1:8000/api/v1/customer/`.

---

### 2. Main FastAPI App Assembly ([`app.py`](file:///c:/Users/JoseMyrsonOBeros/Documents/Python/Mini%20Projects/Order%20Management%20System/backend/src/backend/app.py))

```python
from fastapi import FastAPI
from backend.controller.CustomerController import router as customer_router

app = FastAPI()

# Mount the CustomerController router onto the main app
app.include_router(customer_router)
```

#### How Mounting Works:
- `app.include_router(customer_router)` registers the routes in FastAPI's internal URL routing table. Without this line, FastAPI would return `404 Not Found` for any request to `/api/v1/customer`.

---

### 3. The CLI HTTP Client ([`user_interface.py`](file:///c:/Users/JoseMyrsonOBeros/Documents/Python/Mini%20Projects/Order%20Management%20System/backend/src/backend/interface/user_interface.py))

```python
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1/customer"

def customer_interface():
    ...
    # Sending HTTP POST request over network to API Controller
    response = httpx.post(f"{BASE_URL}/", json=payload, timeout=5.0)

    if response.status_code == 201:
        print("[API 201 SUCCESS] Customer created!")
```

#### Why use `httpx` instead of calling functions directly?
1. **Real-World Simulation**: This mimics how web frontends (React, Vue, Angular) or mobile apps (Flutter, iOS, Android) consume a REST API.
2. **Independent Testing**: You can test the exact same backend endpoints via `httpx` CLI, Postman, or the interactive Swagger docs at `http://127.0.0.1:8000/docs`.

---

### 4. Main Menu & Authentication ([`main_interface.py`](file:///c:/Users/JoseMyrsonOBeros/Documents/Python/Mini%20Projects/Order%20Management%20System/backend/src/backend/interface/main_interface.py))

```python
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1/customer"

def main_interface():
    current_user = None

    while True:
        if current_user is None:
            # Login: Fetch customer list from API and verify credentials
            response = httpx.get(f"{BASE_URL}/")
            customers = response.json()
            ...
        else:
            # Logged-In Menu: Open Customer Management or Logout
            ...
```

---

### 5. Multithreaded Execution ([`main.py`](file:///c:/Users/JoseMyrsonOBeros/Documents/Python/Mini%20Projects/Order%20Management%20System/backend/main.py))

```python
import threading, time, uvicorn
from backend.interface.main_interface import main_interface

def start_api_server():
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    # 1. Start FastAPI server in background thread
    threading.Thread(target=start_api_server, daemon=True).start()
    
    # 2. Wait 1.5s for port 8000 binding
    time.sleep(1.5)

    # 3. Launch CLI Client Interface
    main_interface()
```

#### Why Multithreading?
- Ordinarily, `uvicorn.run()` blocks execution forever while listening for HTTP requests.
- By running `uvicorn` in a background daemon thread (`daemon=True`), the main thread is free to run `main_interface()`, allowing the client and server to run simultaneously in one terminal command!

---

## 💡 Summary of Benefits

| Aspect | Direct Python Call | API Integration (`httpx` + FastAPI) |
| :--- | :--- | :--- |
| **Coupling** | Tightly coupled to Python codebase | Completely decoupled via standard HTTP |
| **Reusability** | Only usable inside Python scripts | Usable by web apps, mobile apps, Postman |
| **Validation** | Manual in-script checks | Automatic Pydantic validation & HTTP status codes |
| **Documentation**| None | Auto-generated OpenAPI / Swagger docs at `/docs` |
