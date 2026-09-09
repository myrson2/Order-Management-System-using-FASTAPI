
import sys
import time
import threading
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from backend.interface.app_interface import main_interface

sys.path.insert(0, str(Path(__file__).parent / "src"))
load_dotenv()

def start_api_server() -> None:
    """
    Description / Purpose:
        Launches the FastAPI Uvicorn ASGI web server on localhost port 8000 in a background daemon thread.

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Runs as a daemon thread to allow simultaneous execution of the CLI client interface.
    """
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8001, log_level="warning")

if __name__ == "__main__":
    # 1. Start server in background thread
    server_thread = threading.Thread(target=start_api_server, daemon=True)
    server_thread.start()

    # 2. Wait briefly for server to bind port 8000
    time.sleep(1.5)

    # 3. Launch Main CLI Interface
    main_interface()
