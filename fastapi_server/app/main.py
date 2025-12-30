import asyncio
import os
from pathlib import Path
from polyglot_server.server import init, start
from polyglot_server.autoload_routes import autoload_routes

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
        "load_env": str(BASE_DIR / "config" / "environment"),
        "lifecycle": str(BASE_DIR / "config" / "lifecycle"),
        "routes": str(BASE_DIR / "routes")
    }
}

# Create app at module level for uvicorn to import
app = init(config)

# Load routes at module level for uvicorn --reload compatibility
autoload_routes(app, config.get("bootstrap", {}))

if __name__ == "__main__":
    # Start (Bootstrap + Serve)
    asyncio.run(start(app, config))
