"""
FastAPI Integration Example for Runtime Template Resolver

This example demonstrates:
- Dependency injection of the template resolver
- Request-scoped template resolution
- Configuration template resolution
- Email/notification templating
- API response templating
"""
import sys
import os
from typing import Annotated, Any, Dict

# Add parent src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel

from runtime_template_resolver import (
    TemplateResolver,
    ResolverOptions,
    MissingStrategy,
)
from runtime_template_resolver.integrations.fastapi_utils import (
    create_resolver_dependency,
    ConfiguredResolverProtocol,
)


# =============================================================================
# Application Configuration (simulated app-yaml style config)
# =============================================================================
APP_CONFIG = {
    "app": {
        "name": "Template Resolver Demo",
        "version": "1.0.0"
    },
    "database": {
        "url": "postgres://{{db.host}}:{{db.port}}/{{db.name}}",
        "pool_size": 10
    },
    "email": {
        "templates": {
            "welcome": "Welcome to {{app.name}}, {{user.name}}!",
            "order_confirmation": "Your order #{{order.id}} for ${{order.total}} has been confirmed.",
            "password_reset": "Click here to reset your password: {{reset_url}}"
        }
    },
    "api": {
        "base_url": "https://{{api.domain}}/v{{api.version}}"
    }
}

# Runtime context that would come from environment/secrets
RUNTIME_CONTEXT = {
    "db": {"host": "localhost", "port": "5432", "name": "demo_db"},
    "api": {"domain": "api.example.com", "version": "2"},
    "app": {"name": "Template Resolver Demo"}
}


# =============================================================================
# Request/Response Models
# =============================================================================
class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


class ResolveRequest(BaseModel):
    template: str
    context: Dict[str, Any]


class ResolveResponse(BaseModel):
    original: str
    resolved: str


class EmailRequest(BaseModel):
    template_name: str
    recipient: str
    context: Dict[str, Any]


class EmailResponse(BaseModel):
    to: str
    subject: str
    body: str


class ConfigResponse(BaseModel):
    database_url: str
    api_base_url: str
    pool_size: int


# =============================================================================
# Application Setup
# =============================================================================
app = FastAPI(
    title="Runtime Template Resolver Demo",
    description="Demonstrates template resolution in a FastAPI application",
    version="1.0.0"
)

# Create resolver dependency with default options
get_resolver = create_resolver_dependency(
    options=ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
)

# Pre-resolve static configuration at startup
_resolver = TemplateResolver()
_resolved_config = _resolver.resolve_object(APP_CONFIG, RUNTIME_CONTEXT)


# =============================================================================
# Custom Dependencies
# =============================================================================
def get_resolved_config() -> Dict[str, Any]:
    """Dependency that provides resolved application configuration."""
    return _resolved_config


def get_user_context(request: Request) -> Dict[str, Any]:
    """
    Dependency that builds user context from request.
    In a real app, this would extract user info from auth token.
    """
    # Simulated user context
    return {
        "user": {
            "id": "user-123",
            "name": "Demo User",
            "email": "demo@example.com"
        },
        "request": {
            "ip": request.client.host if request.client else "unknown",
            "path": str(request.url.path)
        }
    }


# =============================================================================
# Routes
# =============================================================================
@app.get("/health", response_model=HealthResponse)
async def health_check(
    config: Annotated[Dict[str, Any], Depends(get_resolved_config)]
):
    """Health check endpoint with resolved app info."""
    return HealthResponse(
        status="ok",
        app_name=config["app"]["name"],
        version=config["app"]["version"]
    )


@app.get("/config", response_model=ConfigResponse)
async def get_config(
    config: Annotated[Dict[str, Any], Depends(get_resolved_config)]
):
    """Returns resolved configuration (demonstrates startup resolution)."""
    return ConfigResponse(
        database_url=config["database"]["url"],
        api_base_url=config["api"]["base_url"],
        pool_size=config["database"]["pool_size"]
    )


@app.post("/resolve", response_model=ResolveResponse)
async def resolve_template(
    request: ResolveRequest,
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)]
):
    """
    Resolve a template with provided context.

    Example:
    ```json
    {
        "template": "Hello {{name}}, your balance is ${{balance}}",
        "context": {"name": "Alice", "balance": "100.00"}
    }
    ```
    """
    resolved = resolver.resolve(request.template, request.context)
    return ResolveResponse(original=request.template, resolved=resolved)


@app.post("/resolve-object")
async def resolve_object_endpoint(
    data: Dict[str, Any],
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)],
    user_ctx: Annotated[Dict[str, Any], Depends(get_user_context)]
):
    """
    Resolve templates within a nested object structure.
    Automatically includes user context.

    Example:
    ```json
    {
        "greeting": "Hello {{user.name}}!",
        "info": {
            "path": "You are at {{request.path}}"
        }
    }
    ```
    """
    resolved = resolver.resolve_object(data, user_ctx)
    return {"original": data, "resolved": resolved, "context_used": user_ctx}


@app.post("/email/preview", response_model=EmailResponse)
async def preview_email(
    request: EmailRequest,
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)],
    config: Annotated[Dict[str, Any], Depends(get_resolved_config)]
):
    """
    Preview an email using a named template.

    Available templates: welcome, order_confirmation, password_reset

    Example:
    ```json
    {
        "template_name": "welcome",
        "recipient": "user@example.com",
        "context": {"user": {"name": "Alice"}}
    }
    ```
    """
    templates = config["email"]["templates"]

    if request.template_name not in templates:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown template: {request.template_name}. "
                   f"Available: {list(templates.keys())}"
        )

    # Merge app context with request context
    full_context = {**RUNTIME_CONTEXT, **request.context}
    template = templates[request.template_name]
    body = resolver.resolve(template, full_context)

    # Generate subject based on template name
    subjects = {
        "welcome": "Welcome to {{app.name}}!",
        "order_confirmation": "Order #{{order.id}} Confirmed",
        "password_reset": "Password Reset Request"
    }
    subject = resolver.resolve(subjects.get(request.template_name, "Notification"), full_context)

    return EmailResponse(
        to=request.recipient,
        subject=subject,
        body=body
    )


@app.get("/demo/greeting")
async def demo_greeting(
    name: str = "World",
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)] = None
):
    """Simple demo endpoint showing basic template resolution."""
    template = "Hello, {{name}}! Welcome to our API."
    result = resolver.resolve(template, {"name": name})
    return {"message": result}


@app.get("/demo/user-info")
async def demo_user_info(
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)],
    user_ctx: Annotated[Dict[str, Any], Depends(get_user_context)]
):
    """Demo endpoint showing user context injection."""
    template = "User {{user.name}} ({{user.email}}) accessing from {{request.ip}}"
    result = resolver.resolve(template, user_ctx)
    return {"message": result, "context": user_ctx}


# =============================================================================
# Startup Event
# =============================================================================
@app.on_event("startup")
async def startup_event():
    """Log resolved configuration on startup."""
    print("=" * 60)
    print("FastAPI Template Resolver Demo - Starting")
    print("=" * 60)
    print(f"Database URL: {_resolved_config['database']['url']}")
    print(f"API Base URL: {_resolved_config['api']['base_url']}")
    print("=" * 60)


# =============================================================================
# Main Entry Point
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
