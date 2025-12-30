"""
FastAPI Integration Example

Demonstrates how to integrate AppYamlConfig into a FastAPI server using Dependency Injection.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Depends

# In a real package, these would be absolute imports
import sys
project_root = Path(__file__).parent.parent.parent / "src"
sys.path.append(str(project_root))

from app_yaml_static_config.core import AppYamlConfig
from app_yaml_static_config.types import InitOptions

FIXTURES_DIR = Path(__file__).parent.parent.parent / "__fixtures__"


# =============================================================================
# 1. Lifespan for Initialization
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize config (simulated for this example using fixtures)
    config_file = FIXTURES_DIR / "base.yaml"
    print(f"Loading config from: {config_file}")
    
    options = InitOptions(
        files=[str(config_file)],
        config_dir=str(FIXTURES_DIR)
    )
    AppYamlConfig.initialize(options)
    
    yield
    # Cleanup if necessary


app = FastAPI(lifespan=lifespan)


# =============================================================================
# 2. Dependency for Config Injection
# =============================================================================

def get_config() -> AppYamlConfig:
    """Dependency that returns the AppYamlConfig singleton."""
    return AppYamlConfig.get_instance()


ConfigDep = Annotated[AppYamlConfig, Depends(get_config)]


# =============================================================================
# 3. Routes
# =============================================================================

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/demo/config")
async def get_demo_config(config: ConfigDep):
    """
    Demonstrates accessing configuration via dependency injection.
    """
    app_name = config.get_nested("app", "name")
    environment = config.get_nested("app", "environment", default="unknown")
    
    return {
        "message": "Configuration accessed successfully via dependency injection",
        "appName": app_name,
        "environment": environment
    }

if __name__ == "__main__":
    import uvicorn
    # Use imported app to avoid reload issues in some envs, but string ref is better
    uvicorn.run("examples.fastapi_app.main:app", host="0.0.0.0", port=8000, reload=True)

