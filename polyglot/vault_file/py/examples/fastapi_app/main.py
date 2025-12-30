import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Boilerplate (in real usage, package would be installed)
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from vault_file import VaultFileSDK, EnvStore

DEMO_ENV_FILE = os.path.join(os.path.dirname(__file__), ".env.demo")

# Setup demo file
if not os.path.exists(DEMO_ENV_FILE):
    with open(DEMO_ENV_FILE, "w") as f:
        f.write("SERVER_PORT=8000\\nAPI_KEY=secret_abc_123\\n")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("Initialize EnvStore before server start...")
    sdk = VaultFileSDK.create().with_env_path(DEMO_ENV_FILE).build()
    
    sdk.load_config()
    
    yield
    
    # --- Shutdown ---
    if os.path.exists(DEMO_ENV_FILE):
        os.remove(DEMO_ENV_FILE)
    print("Cleanup complete.")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "initialized": EnvStore.is_initialized()
    }

@app.get("/config-demo")
async def config_demo():
    # Demonstration of accessing config
    return {
        "port_configured": EnvStore.get("SERVER_PORT"),
        "api_key_masked": "***" if EnvStore.get("API_KEY") else "missing"
    }

if __name__ == "__main__":
    import uvicorn
    # Note: Port here is just for running uvicorn, unrelated to logic demo
    uvicorn.run(app, host="0.0.0.0", port=8000)
