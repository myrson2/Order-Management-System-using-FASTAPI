
import sys
import time
import threading
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from backend.interface.app_interface import app_interface

sys.path.insert(0, str(Path(__file__).parent / "src"))
load_dotenv()

def start_api_server():
    """Starts the FastAPI Uvicorn server in background."""
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    # 1. Start server in background thread
    server_thread = threading.Thread(target=start_api_server, daemon=True)
    server_thread.start()

    # 2. Wait briefly for server to bind port 8000
    time.sleep(1.5)

    # 3. Launch Main CLI Interface
    app_interface()
