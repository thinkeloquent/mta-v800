# Server Integration Guide - Python (FastAPI)

This guide covers integrating App YAML Static Config with FastAPI applications.

## FastAPI Integration

### Pattern: Lifespan Context Manager

The recommended approach uses FastAPI's lifespan context manager to initialize configuration at startup.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app_yaml_static_config import AppYamlConfig, AppYamlConfigSDK
from app_yaml_static_config.types import InitOptions
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize configuration
    config_dir = os.getenv('CONFIG_DIR', './config')
    env = os.getenv('APP_ENV', 'development')

    options = InitOptions(
        files=[
            os.path.join(config_dir, 'base.yaml'),
            os.path.join(config_dir, f'{env}.yaml')
        ],
        config_dir=config_dir,
        app_env=env
    )

    AppYamlConfig.initialize(options)
    config = AppYamlConfig.get_instance()

    # Store in app state
    app.state.config = config
    app.state.sdk = AppYamlConfigSDK(config)

    print(f"Configuration loaded: {app.state.sdk.list_providers()}")

    yield

    # Shutdown: Cleanup if needed
    pass

app = FastAPI(lifespan=lifespan)
```

### Route Handlers

Access configuration through `request.app.state`:

```python
from fastapi import Request

@app.get("/health")
async def health(request: Request):
    return {
        "status": "ok",
        "app_name": request.app.state.config.get_nested("app", "name"),
        "version": request.app.state.config.get_nested("app", "version")
    }

@app.get("/config")
async def get_config(request: Request):
    return request.app.state.sdk.get_all()

@app.get("/config/{key}")
async def get_config_key(key: str, request: Request):
    return {
        "key": key,
        "value": request.app.state.sdk.get(key)
    }

@app.get("/providers")
async def list_providers(request: Request):
    return {"providers": request.app.state.sdk.list_providers()}

@app.get("/services")
async def list_services(request: Request):
    return {"services": request.app.state.sdk.list_services()}

@app.get("/storages")
async def list_storages(request: Request):
    return {"storages": request.app.state.sdk.list_storages()}
```

### Pattern: Dependency Injection

Use FastAPI's dependency injection for cleaner route handlers:

```python
from fastapi import Depends, Request
from app_yaml_static_config import AppYamlConfig, AppYamlConfigSDK

def get_config(request: Request) -> AppYamlConfig:
    """Dependency to get configuration instance."""
    return request.app.state.config

def get_sdk(request: Request) -> AppYamlConfigSDK:
    """Dependency to get SDK instance."""
    return request.app.state.sdk

@app.get("/database")
async def get_database_config(config: AppYamlConfig = Depends(get_config)):
    return config.get_nested("services", "database")

@app.get("/providers/{provider}")
async def get_provider(provider: str, sdk: AppYamlConfigSDK = Depends(get_sdk)):
    providers = sdk.get("providers") or {}
    if provider not in providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    return providers[provider]
```

### Complete Example

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from app_yaml_static_config import AppYamlConfig, AppYamlConfigSDK
from app_yaml_static_config.types import InitOptions
import os

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    config_dir = os.getenv('CONFIG_DIR', './config')
    options = InitOptions(
        files=[os.path.join(config_dir, 'base.yaml')],
        config_dir=config_dir
    )
    AppYamlConfig.initialize(options)
    app.state.config = AppYamlConfig.get_instance()
    app.state.sdk = AppYamlConfigSDK(app.state.config)
    yield

# Create app
app = FastAPI(
    title="My API",
    lifespan=lifespan
)

# Dependencies
def get_sdk(request: Request) -> AppYamlConfigSDK:
    return request.app.state.sdk

# Routes
@app.get("/health")
async def health(request: Request):
    return {
        "status": "ok",
        "app_name": request.app.state.config.get_nested("app", "name")
    }

@app.get("/providers")
async def list_providers(sdk: AppYamlConfigSDK = Depends(get_sdk)):
    return {"providers": sdk.list_providers()}

@app.get("/services")
async def list_services(sdk: AppYamlConfigSDK = Depends(get_sdk)):
    return {"services": sdk.list_services()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Testing

Use TestClient with configuration mocking:

```python
import pytest
from fastapi.testclient import TestClient
from app_yaml_static_config.core import AppYamlConfig

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset AppYamlConfig singleton before each test."""
    AppYamlConfig._instance = None
    AppYamlConfig._config = {}
    AppYamlConfig._original_configs = {}
    AppYamlConfig._initial_merged_config = None
    yield
    AppYamlConfig._instance = None
    AppYamlConfig._config = {}
    AppYamlConfig._original_configs = {}
    AppYamlConfig._initial_merged_config = None

@pytest.fixture
def client():
    from main import app
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_providers_endpoint(client):
    response = client.get("/providers")
    assert response.status_code == 200
    assert isinstance(response.json()["providers"], list)
```

## Best Practices

1. **Initialize in Lifespan**: Always initialize configuration during startup
2. **Use app.state**: Store config/SDK in app.state for global access
3. **Dependency Injection**: Use `Depends()` for cleaner route handlers
4. **Environment Variables**: Load environment-specific config files
5. **Immutability**: Never attempt to modify configuration at runtime
