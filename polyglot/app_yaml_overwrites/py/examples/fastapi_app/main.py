"""
FastAPI Integration Example for app_yaml_overwrites
====================================================

This example demonstrates how to integrate app_yaml_overwrites with FastAPI:
- Dependency injection for configuration access
- Context building with request-scoped data
- Health check endpoints
- Provider configuration endpoints

Run with: uvicorn fastapi_app.main:app --reload --port 8000
"""

import os
import sys
from typing import Annotated, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, HTTPException
from pydantic import BaseModel

# Add parent src to path for direct execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'app_yaml_overwrites'))

# Import directly from modules (bypassing __init__.py which has external deps)
from logger import Logger
from context_builder import ContextBuilder
from overwrite_merger import apply_overwrites


# =============================================================================
# Configuration (Mock - would use ConfigSDK in production)
# =============================================================================

# Mock configuration simulating what AppYamlConfig would provide
MOCK_CONFIG = {
    "app": {
        "name": "FastAPI Example",
        "version": "1.0.0",
        "environment": "development"
    },
    "providers": {
        "user_api": {
            "base_url": "https://users.example.com",
            "timeout": 30,
            "headers": {
                "Content-Type": "application/json",
                "Authorization": None,
                "X-Request-Id": None
            },
            "overwrite_from_context": {
                "headers": {
                    "Authorization": "Bearer {{auth.token}}",
                    "X-Request-Id": "{{request.headers.x-request-id}}"
                }
            }
        },
        "payment_api": {
            "base_url": "https://payments.example.com",
            "timeout": 60,
            "headers": {
                "X-Api-Key": None,
                "X-Tenant-Id": None
            },
            "overwrite_from_context": {
                "headers": {
                    "X-Api-Key": "{{env.PAYMENT_API_KEY}}",
                    "X-Tenant-Id": "{{tenant.id}}"
                }
            }
        }
    },
    "features": {
        "enable_caching": True,
        "cache_ttl": 3600
    }
}

# Create logger
logger = Logger.create("fastapi-example", "main.py")


# =============================================================================
# Application State
# =============================================================================

class AppState:
    """Application state container."""
    config: Dict[str, Any] = MOCK_CONFIG
    request_count: int = 0


app_state = AppState()


# =============================================================================
# Context Extenders
# =============================================================================

async def auth_extender(ctx: Dict[str, Any], request: Any) -> Dict[str, Any]:
    """Extract auth context from request headers."""
    auth_header = None
    if request and hasattr(request, "headers"):
        auth_header = request.headers.get("authorization", "")

    return {
        "auth": {
            "token": auth_header.replace("Bearer ", "") if auth_header else None,
            "authenticated": bool(auth_header)
        }
    }


async def tenant_extender(ctx: Dict[str, Any], request: Any) -> Dict[str, Any]:
    """Extract tenant context from request headers."""
    tenant_id = None
    if request and hasattr(request, "headers"):
        tenant_id = request.headers.get("x-tenant-id", "default")

    return {
        "tenant": {
            "id": tenant_id,
            "name": f"Tenant {tenant_id}"
        }
    }


# =============================================================================
# Dependencies
# =============================================================================

async def get_config() -> Dict[str, Any]:
    """Dependency: Get raw configuration."""
    return app_state.config


async def get_context(request: Request) -> Dict[str, Any]:
    """Dependency: Build resolution context with request data."""
    # Extract headers as dict for context
    request_headers = dict(request.headers)

    context = await ContextBuilder.build(
        {
            "config": app_state.config,
            "app": app_state.config.get("app", {}),
            "env": dict(os.environ),
            "state": {"request_count": app_state.request_count},
            "request": request
        },
        extenders=[auth_extender, tenant_extender]
    )

    # Add request headers to context for template resolution
    context["request"] = {"headers": request_headers}

    return context


async def get_resolved_provider(
    provider_name: str,
    context: Annotated[Dict[str, Any], Depends(get_context)]
) -> Dict[str, Any]:
    """Dependency: Get a resolved provider configuration."""
    config = app_state.config
    providers = config.get("providers", {})

    if provider_name not in providers:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

    provider = providers[provider_name]
    overwrites = provider.get("overwrite_from_context", {})

    # Simulate template resolution (in production, RuntimeTemplateResolver does this)
    resolved_overwrites = resolve_templates(overwrites, context)

    # Apply overwrites
    resolved = apply_overwrites(provider, resolved_overwrites)

    return resolved


def resolve_templates(obj: Any, context: Dict[str, Any]) -> Any:
    """Simple template resolver for demo purposes."""
    if isinstance(obj, str):
        if obj.startswith("{{") and obj.endswith("}}"):
            path = obj[2:-2].strip()
            return get_nested_value(context, path)
        return obj
    elif isinstance(obj, dict):
        return {k: resolve_templates(v, context) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_templates(item, context) for item in obj]
    return obj


def get_nested_value(obj: Dict[str, Any], path: str) -> Any:
    """Get nested value from dict using dot notation."""
    keys = path.split(".")
    value = obj
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value


# =============================================================================
# Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting FastAPI example application")
    logger.debug("Configuration loaded", app_name=MOCK_CONFIG["app"]["name"])
    yield
    logger.info("Shutting down FastAPI example application")


# =============================================================================
# Application
# =============================================================================

app = FastAPI(
    title="app_yaml_overwrites FastAPI Example",
    description="Demonstrates integration of app_yaml_overwrites with FastAPI",
    version="1.0.0",
    lifespan=lifespan
)


# =============================================================================
# Response Models
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    request_count: int


class ConfigResponse(BaseModel):
    app: Dict[str, Any]
    features: Dict[str, Any]
    provider_names: list[str]


class ProviderResponse(BaseModel):
    name: str
    base_url: str
    timeout: int
    headers: Dict[str, Optional[str]]
    resolved: bool


class ContextResponse(BaseModel):
    keys: list[str]
    app: Dict[str, Any]
    auth: Dict[str, Any]
    tenant: Dict[str, Any]


# =============================================================================
# Routes
# =============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(config: Annotated[Dict[str, Any], Depends(get_config)]):
    """Health check endpoint with app information."""
    app_state.request_count += 1

    return HealthResponse(
        status="healthy",
        app_name=config["app"]["name"],
        version=config["app"]["version"],
        request_count=app_state.request_count
    )


@app.get("/config", response_model=ConfigResponse, tags=["Configuration"])
async def get_configuration(config: Annotated[Dict[str, Any], Depends(get_config)]):
    """Get application configuration (non-sensitive)."""
    logger.info("Configuration requested")

    return ConfigResponse(
        app=config["app"],
        features=config["features"],
        provider_names=list(config["providers"].keys())
    )


@app.get("/context", response_model=ContextResponse, tags=["Configuration"])
async def get_current_context(
    request: Request,
    context: Annotated[Dict[str, Any], Depends(get_context)]
):
    """Get current resolution context (for debugging)."""
    logger.debug("Context requested", keys=list(context.keys()))

    return ContextResponse(
        keys=list(context.keys()),
        app=context.get("app", {}),
        auth=context.get("auth", {}),
        tenant=context.get("tenant", {})
    )


@app.get("/providers/{provider_name}", response_model=ProviderResponse, tags=["Providers"])
async def get_provider(
    provider_name: str,
    request: Request,
    context: Annotated[Dict[str, Any], Depends(get_context)]
):
    """
    Get resolved provider configuration.

    Headers used for resolution:
    - Authorization: Bearer token for auth context
    - X-Tenant-Id: Tenant identifier
    - X-Request-Id: Request correlation ID
    """
    logger.info("Provider requested", provider=provider_name)

    config = app_state.config
    providers = config.get("providers", {})

    if provider_name not in providers:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

    provider = providers[provider_name]
    overwrites = provider.get("overwrite_from_context", {})

    # Resolve templates
    resolved_overwrites = resolve_templates(overwrites, context)

    # Apply overwrites
    resolved = apply_overwrites(provider, resolved_overwrites)

    return ProviderResponse(
        name=provider_name,
        base_url=resolved["base_url"],
        timeout=resolved["timeout"],
        headers=resolved["headers"],
        resolved=True
    )


@app.get("/providers/{provider_name}/raw", response_model=ProviderResponse, tags=["Providers"])
async def get_provider_raw(
    provider_name: str,
    config: Annotated[Dict[str, Any], Depends(get_config)]
):
    """Get raw (unresolved) provider configuration."""
    providers = config.get("providers", {})

    if provider_name not in providers:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

    provider = providers[provider_name]

    return ProviderResponse(
        name=provider_name,
        base_url=provider["base_url"],
        timeout=provider["timeout"],
        headers=provider["headers"],
        resolved=False
    )


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
