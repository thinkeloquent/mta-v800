# Server Integration Guide for FastAPI

## FastAPI Integration (Python)

The integration relies on Uvicorn for execution, with the `server` module wrapping the configuration.

### Standard Usage

In `app/main.py`:

```python
import asyncio
from server import init, start

config = {
    "title": "My Polyglot App",
    "port": 8080,
    "bootstrap": {
        "load_env": "./config/env",
        "lifecycle": "./config/lifecycle"
    }
}

if __name__ == "__main__":
    # 1. Init
    app = init(config)
    
    # 2. Start (Bootstrap + Serve)
    asyncio.run(start(app, config))
```

### Lifespan Context Manager

The server uses `asynccontextmanager` to handle the startup and shutdown phases.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    # - Runs registered functionality from lifecycle modules
    yield
    # Shutdown phase
    # - Runs cleanup tasks
```

This ensures compatibility with Uvicorn's signal handling mechanisms.
