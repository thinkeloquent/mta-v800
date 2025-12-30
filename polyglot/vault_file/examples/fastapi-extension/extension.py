from contextlib import asynccontextmanager
from fastapi import FastAPI
from vault_file import EnvStore

@asynccontextmanager
async def vault_lifespan(app: FastAPI):
    """
    Lifespan context manager that initializes the Vault File EnvStore
    on application startup.
    """
    try:
        result = EnvStore.on_startup()
        print(f"[INFO] Vault File initialized. Loaded {result.total_vars_loaded} variables.")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Vault File: {e}")
        raise e
    yield

# Usage example:
# app = FastAPI(lifespan=vault_lifespan)
