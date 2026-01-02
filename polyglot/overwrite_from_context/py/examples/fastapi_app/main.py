"""
Runtime Template Resolver - FastAPI Integration Example

This example demonstrates how to integrate the runtime_template_resolver
package with a FastAPI application, including:
- Configuration resolution at startup
- Request-scoped resolution
- Dependency injection patterns
- Health check and demo routes

Run with: uvicorn examples.fastapi_app.main:app --reload --port 8000
"""
import os
from contextlib import asynccontextmanager
from typing import Annotated, Any, Dict
from datetime import datetime

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

from runtime_template_resolver import ComputeScope, create_registry, create_resolver
from runtime_template_resolver.integrations.fastapi import resolve_startup, get_request_config


# =============================================================================
# Mock Configuration (simulating app.yaml)
# =============================================================================
MOCK_APP_CONFIG = {
    "app": {
        "name": "{{env.APP_NAME | 'FastAPI Demo'}}",
        "version": "{{fn:get_app_version}}",
        "environment": "{{env.ENVIRONMENT | 'development'}}",
        "debug": "{{env.DEBUG | 'true'}}"
    },
    "server": {
        "host": "{{env.HOST | '0.0.0.0'}}",
        "port": "{{env.PORT | '8000'}}"
    },
    "database": {
        "connection": "{{fn:build_connection_string}}",
        "pool_size": "{{env.DB_POOL_SIZE | '5'}}",
        "timeout": "{{env.DB_TIMEOUT | '30'}}"
    },
    "features": {
        "auth_enabled": "{{env.AUTH_ENABLED | 'false'}}",
        "metrics_enabled": "{{env.METRICS_ENABLED | 'true'}}",
        "rate_limit": "{{env.RATE_LIMIT | '100'}}"
    },
    "metadata": {
        "started_at": "{{fn:get_startup_time}}"
    }
}


# =============================================================================
# Compute Registry Setup
# =============================================================================
registry = create_registry()

# STARTUP scope functions (cached, run once)
registry.register(
    "get_app_version",
    lambda ctx=None: "1.2.3-demo",
    ComputeScope.STARTUP
)

registry.register(
    "get_startup_time",
    lambda ctx=None: datetime.utcnow().isoformat() + "Z",
    ComputeScope.STARTUP
)

registry.register(
    "build_connection_string",
    lambda ctx: (
        f"postgresql://"
        f"{ctx.get('env', {}).get('DB_USER', 'app')}:"
        f"{ctx.get('env', {}).get('DB_PASSWORD', 'secret')}@"
        f"{ctx.get('env', {}).get('DB_HOST', 'localhost')}:"
        f"{ctx.get('env', {}).get('DB_PORT', '5432')}/"
        f"{ctx.get('env', {}).get('DB_NAME', 'demo_db')}"
    ),
    ComputeScope.STARTUP
)

# REQUEST scope functions (run per-request)
_request_counter = {"value": 0}


def generate_request_id(ctx):
    """Generate unique request ID for each request."""
    _request_counter["value"] += 1
    return f"req-{_request_counter['value']:08d}"


registry.register("get_request_id", generate_request_id, ComputeScope.REQUEST)


# =============================================================================
# FastAPI Application with Lifespan
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    STARTUP: Resolve configuration at application startup.
    SHUTDOWN: Cleanup if needed.
    """
    print("[STARTUP] Resolving configuration...")

    # Resolve configuration at STARTUP scope
    await resolve_startup(
        app,
        config=MOCK_APP_CONFIG,
        registry=registry,
        state_property="config"
    )

    print(f"[STARTUP] App: {app.state.config['app']['name']}")
    print(f"[STARTUP] Version: {app.state.config['app']['version']}")
    print(f"[STARTUP] Environment: {app.state.config['app']['environment']}")
    print("[STARTUP] Configuration resolved successfully!")

    yield

    # Shutdown cleanup
    print("[SHUTDOWN] Application shutting down...")


app = FastAPI(
    title="Runtime Template Resolver Demo",
    description="Demonstrates runtime_template_resolver integration with FastAPI",
    version="1.0.0",
    lifespan=lifespan
)


# =============================================================================
# Type Alias for Dependency Injection
# =============================================================================
ResolvedConfig = Annotated[Dict[str, Any], Depends(get_request_config)]


# =============================================================================
# Routes
# =============================================================================
@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns basic health status and startup configuration.
    """
    return {
        "status": "healthy",
        "app": app.state.config["app"]["name"],
        "version": app.state.config["app"]["version"],
        "environment": app.state.config["app"]["environment"]
    }


@app.get("/config")
async def get_config(config: ResolvedConfig):
    """
    Get resolved configuration.

    This endpoint demonstrates REQUEST-scope resolution where
    the entire configuration is re-resolved with request context.
    """
    return {
        "resolved_at": "request",
        "config": config
    }


@app.get("/config/startup")
async def get_startup_config():
    """
    Get STARTUP-resolved configuration (cached).

    This shows the configuration as it was resolved at application startup.
    """
    return {
        "resolved_at": "startup",
        "config": app.state.config
    }


@app.get("/request-id")
async def get_request_id(request: Request):
    """
    Get unique request ID using resolver.

    Demonstrates using resolver directly for REQUEST-scope functions.
    """
    resolver = request.app.state._context_resolver

    # Resolve REQUEST-scope function
    request_id = await resolver.resolve(
        "{{fn:get_request_id}}",
        {"env": dict(os.environ), "request": request},
        scope=ComputeScope.REQUEST
    )

    return {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path
    }


@app.get("/demo/features")
async def get_features(config: ResolvedConfig):
    """
    Get feature flags from resolved configuration.

    Demonstrates accessing specific configuration sections.
    """
    return {
        "features": config["features"],
        "note": "Feature flags are resolved from environment variables with defaults"
    }


@app.get("/demo/database")
async def get_database_info(config: ResolvedConfig):
    """
    Get database configuration (sanitized).

    Demonstrates accessing database config with password redaction.
    """
    db_config = config["database"]

    # Sanitize connection string (redact password)
    conn_str = db_config["connection"]
    if "@" in conn_str:
        # Redact password between :// and @
        parts = conn_str.split("://", 1)
        if len(parts) == 2:
            auth_and_rest = parts[1].split("@", 1)
            if len(auth_and_rest) == 2 and ":" in auth_and_rest[0]:
                user = auth_and_rest[0].split(":")[0]
                conn_str = f"{parts[0]}://{user}:****@{auth_and_rest[1]}"

    return {
        "connection": conn_str,
        "pool_size": db_config["pool_size"],
        "timeout": db_config["timeout"]
    }


@app.get("/demo/resolve")
async def demo_resolve(
    request: Request,
    pattern: str = "{{env.HOME | '/home/user'}}"
):
    """
    Demo endpoint to resolve arbitrary patterns.

    Query parameter 'pattern' can be a template or compute pattern.

    Examples:
    - /demo/resolve?pattern={{env.USER | 'anonymous'}}
    - /demo/resolve?pattern={{env.PATH | '/usr/bin'}}
    """
    resolver = request.app.state._context_resolver

    try:
        result = await resolver.resolve(
            pattern,
            {"env": dict(os.environ)},
            scope=ComputeScope.REQUEST
        )
        return {
            "pattern": pattern,
            "resolved": result,
            "type": type(result).__name__
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "pattern": pattern,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )


# =============================================================================
# Error Handler
# =============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "type": type(exc).__name__,
            "path": request.url.path
        }
    )


# =============================================================================
# Main Entry Point
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    print("Starting FastAPI Demo Server...")
    print("Visit http://localhost:8000/docs for API documentation")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
