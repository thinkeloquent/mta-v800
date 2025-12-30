import asyncio
import os
from pathlib import Path
from app.server import init, start

# Determine paths relative to this file
# Assuming structure:
# root/
#   app/main.py
#   config/
#     env/
#     lifecycle/
BASE_DIR = Path(__file__).resolve().parent.parent

config = {
    "title": "FastAPI Integrated Server",
    "port": 8080,
    "bootstrap": {
        "load_env": str(BASE_DIR / "config" / "env"),
        "lifecycle": str(BASE_DIR / "config" / "lifecycle")
    }
}

# Create app at module level for uvicorn to import
app = init(config)

if __name__ == "__main__":
    # Start (Bootstrap + Serve)
    asyncio.run(start(app, config))
