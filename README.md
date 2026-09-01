# 📦 Order Management System (Backend)

An educational backend application built with **FastAPI**, **Pydantic v2**, and **Python 3.14+**. 

This project serves as a hands-on learning environment for mastering modern Python web backend development, data validation with Pydantic, clean layered architecture, and HTTP client-server interactions.

---

## 🎯 Project Purpose & Background

The primary goal of this project is to learn and demonstrate core backend development concepts using the modern Python ecosystem:

- **FastAPI Framework**: Defining RESTful API controllers, route handlers, and dependency injection.
- **Pydantic v2 Schemas**: Utilizing type validation, custom field validators, schema mapping (`to_dict()`, `from_dict()`), and JSON mode serialization (`model_dump(mode='json')`).
- **Layered Software Architecture**: Separating concerns into **Repository** (data access & JSON storage), **Service** (business logic & caching), **Controller** (HTTP routing & API validation), and **Schemas** (data validation models).
- **Client-Server Decoupling**: Building a terminal-based CLI interface (`app_interface.py`) that acts as an independent HTTP client. `httpx` sends requests over the network (`http://127.0.0.1:8000/api/v1/customer`), and the **FastAPI web server** automatically routes and validates those network requests.
- **Multithreaded Execution**: Running the Uvicorn web server in a background thread while concurrently launching an interactive CLI menu in `main.py`.

> 📘 **For a detailed technical walkthrough of the HTTP API integration, see [`API_INTEGRATION_GUIDE.md`](file:///c:/Users/JoseMyrsonOBeros/Documents/Python/Mini%20Projects/Order%20Management%20System/backend/API_INTEGRATION_GUIDE.md)**

---

## 🏗️ Architecture & Project Structure

The project follows a clean, modular architecture:

```text
backend/
├── main.py                          # Application entry point (runs API server & CLI menu together)
├── pyproject.toml                   # Dependency & project configuration
├── README.md                        # Project documentation
├── API_INTEGRATION_GUIDE.md         # Detailed API architecture guide
└── src/
    └── backend/
        ├── app.py                   # Main FastAPI app assembly & router registration
        ├── controller/              # HTTP Request handlers & routing (FastAPI APIRouter)
        │   ├── CustomerController.py
        │   └── OrderController.py
        ├── database/                # Persistent JSON storage files
        │   ├── customer.json
        │   └── products.json
        ├── interface/               # Interactive CLI Client (communicates over HTTP via httpx)
        │   └── main_interface.py
        ├── repository/              # Data storage & file access abstractions
        │   └── repositories.py
        ├── schemas/                 # Pydantic data validation schemas
        │   ├── Customer.py
        │   ├── Order.py
        │   └── OrderItems.py
        └── service/                 # Core business logic & caching layer
            └── services.py
```

---

## 🔁 Data Flow Lifecycle

```text
User Terminal Input 
       │
       ▼
[1] main_interface.py  ──(Packs input into Customer schema & converts via to_dict())
       │
       ▼  (HTTP POST / GET request over port 8000 via httpx)
[2] app.py (FastAPI App)
       │
       ▼  (Routes request to controller)
[3] CustomerController.py ──(Validates incoming payload with Pydantic Customer schema)
       │
       ▼
[4] CustomerService & Repository ──(Appends to cache & saves to customer.json file)
       │
       ▼  (Returns HTTP 201 Created / 200 OK JSON response)
[5] main_interface.py  ──(Displays output & session status to user)
```

---

## 💡 Key Conceptual Learnings

### 1. Pydantic `mode='json'` Serialization
When dumping models containing complex types (like `uuid.UUID`), calling `model.model_dump()` retains `UUID` objects in memory, causing `TypeError: Object of type UUID is not JSON serializable` when saving to files with `json.dump()`.
Calling `model.model_dump(mode='json')` in `to_dict()` automatically converts non-standard JSON types into primitive JSON strings (`str`).

### 2. Client-Server Serialization & Validation Pipeline
* **Client (`app_interface.py`)**: `User.py` object $\xrightarrow{\text{to\_dict()}}$ `dict` $\xrightarrow{\text{httpx}}$ JSON Text over HTTP.
* **Server (`CustomerController.py`)**: JSON Text over HTTP $\xrightarrow{\text{customer: Customer}}$ Validated `User.py` object.
* **Storage (`user_services.py` / `repositories.py`)**: `User.py` object $\xrightarrow{\text{to\_dict()}}$ `dict` $\xrightarrow{\text{json.dump()}}$ `customer.json`.

### 3. String Type Rationale for Phone Numbers
Phone numbers are defined as `str` (not `int`) because:
- Preserves leading zeros (e.g., `"09064495279"`).
- Phone numbers are textual identifiers, not mathematical values.
- Supports formatting symbols (`+`, spaces, dashes).
- Enables string-based validation rules (`len() == 11`, `.startswith("09")`).

---

## 🚀 Getting Started

### Prerequisites

- **Python**: `>= 3.14`
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (fast Python package manager)

### Installation

1. Clone the repository and navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

---

## 💻 How to Run

### Option 1: Run Server & CLI Client Together (Recommended)

Run the main application script:

```bash
python main.py
```

This will:
1. Start the **FastAPI Uvicorn server** in a background thread at `http://127.0.0.1:8000`.
2. Automatically launch the interactive **CLI Interface** in your terminal.

---

### Option 2: Run Server and CLI Separately

1. **Start the API Server**:
   ```bash
   python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Run the CLI Client in a second terminal**:
   ```bash
   python src/backend/interface/app_interface.py
   ```

---

## 📑 API Documentation & Swagger UI

FastAPI automatically generates interactive OpenAPI documentation when the server is running.

Open your browser to:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Available Customer Endpoints

| HTTP Method | Route | Description |
| :--- | :--- | :--- |
| **GET** | `/api/v1/customer/` | Retrieve all customers |
| **GET** | `/api/v1/customer/{customer_id}` | Retrieve a single customer by ID |
| **POST** | `/api/v1/customer/` | Create a new customer (validated via Pydantic) |

---

## 🛠️ Key Technologies Used

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern web framework for building APIs.
- **[Pydantic v2](https://docs.pydantic.dev/)**: Data validation and settings management using Python type hints.
- **[Uvicorn](https://www.uvicorn.org/)**: Lightning-fast ASGI server implementation.
- **[HTTPX](https://www.python-httpx.org/)**: Next-generation HTTP client for Python.
- **[uv](https://astral.sh/uv)**: Extremely fast Python package installer and resolver.
