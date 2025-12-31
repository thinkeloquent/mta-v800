# Server Integration Guide - Python (FastAPI)

This guide covers integrating the Runtime Template Resolver with FastAPI applications.

## Overview

The FastAPI integration provides:

- Dependency injection for template resolution
- Request-scoped resolver instances
- Configuration template resolution at startup
- Type-safe resolver protocol

## Installation

```bash
poetry add runtime-template-resolver fastapi uvicorn
```

## Pattern: Dependency Injection

The recommended pattern uses FastAPI's dependency injection system.

### Basic Setup

```python
from fastapi import FastAPI, Depends
from typing import Annotated

from runtime_template_resolver import ResolverOptions, MissingStrategy
from runtime_template_resolver.integrations.fastapi_utils import (
    create_resolver_dependency,
    ConfiguredResolverProtocol,
)

app = FastAPI()

# Create resolver dependency
get_resolver = create_resolver_dependency(
    options=ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
)

@app.get("/greet")
def greet(
    name: str,
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)]
):
    template = "Hello, {{name}}! Welcome to our API."
    result = resolver.resolve(template, {"name": name})
    return {"message": result}
```

### With Custom Options

```python
from runtime_template_resolver import ResolverOptions, MissingStrategy

# Keep missing placeholders
get_resolver_keep = create_resolver_dependency(
    options=ResolverOptions(missing_strategy=MissingStrategy.KEEP)
)

# Strict mode - raise on errors
get_resolver_strict = create_resolver_dependency(
    options=ResolverOptions(
        missing_strategy=MissingStrategy.ERROR,
        throw_on_error=True
    )
)
```

## Pattern: Configuration Resolution at Startup

Resolve configuration templates once at application startup.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from runtime_template_resolver import TemplateResolver

# Configuration with templates
APP_CONFIG = {
    "database": {
        "url": "postgres://{{db.host}}:{{db.port}}/{{db.name}}"
    },
    "api": {
        "base_url": "https://{{api.domain}}/v{{api.version}}"
    }
}

# Runtime context from environment
RUNTIME_CONTEXT = {
    "db": {"host": "localhost", "port": "5432", "name": "myapp"},
    "api": {"domain": "api.example.com", "version": "2"}
}

# Resolve at startup
resolver = TemplateResolver()
resolved_config = resolver.resolve_object(APP_CONFIG, RUNTIME_CONTEXT)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Database URL: {resolved_config['database']['url']}")
    print(f"API Base URL: {resolved_config['api']['base_url']}")
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)

@app.get("/config")
def get_config():
    return {
        "database_url": resolved_config["database"]["url"],
        "api_base_url": resolved_config["api"]["base_url"]
    }
```

## Pattern: Request Context Injection

Inject request-specific context into templates.

```python
from fastapi import FastAPI, Depends, Request
from typing import Annotated, Dict, Any

from runtime_template_resolver.integrations.fastapi_utils import (
    create_resolver_dependency,
    ConfiguredResolverProtocol,
)

app = FastAPI()
get_resolver = create_resolver_dependency()

def get_request_context(request: Request) -> Dict[str, Any]:
    """Build context from request."""
    return {
        "user": {
            "id": "user-123",  # From auth token in real app
            "name": "Demo User"
        },
        "request": {
            "ip": request.client.host if request.client else "unknown",
            "path": str(request.url.path)
        }
    }

@app.get("/user-info")
def user_info(
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)],
    ctx: Annotated[Dict[str, Any], Depends(get_request_context)]
):
    template = "User {{user.name}} accessing {{request.path}} from {{request.ip}}"
    result = resolver.resolve(template, ctx)
    return {"message": result, "context": ctx}
```

## Pattern: Email Templating

Use template resolution for email generation.

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated, Dict, Any

from runtime_template_resolver.integrations.fastapi_utils import (
    create_resolver_dependency,
    ConfiguredResolverProtocol,
)

app = FastAPI()
get_resolver = create_resolver_dependency()

EMAIL_TEMPLATES = {
    "welcome": "Welcome to {{app.name}}, {{user.name}}!",
    "order_confirmation": "Your order #{{order.id}} for ${{order.total}} is confirmed.",
    "password_reset": "Click here to reset: {{reset_url}}"
}

class EmailRequest(BaseModel):
    template_name: str
    recipient: str
    context: Dict[str, Any]

class EmailResponse(BaseModel):
    to: str
    subject: str
    body: str

@app.post("/email/preview", response_model=EmailResponse)
def preview_email(
    request: EmailRequest,
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)]
):
    if request.template_name not in EMAIL_TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown template: {request.template_name}"
        )

    template = EMAIL_TEMPLATES[request.template_name]
    body = resolver.resolve(template, request.context)

    return EmailResponse(
        to=request.recipient,
        subject=f"Template: {request.template_name}",
        body=body
    )
```

## Complete Example Application

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Annotated, Dict, Any

from runtime_template_resolver import TemplateResolver, ResolverOptions, MissingStrategy
from runtime_template_resolver.integrations.fastapi_utils import (
    create_resolver_dependency,
    ConfiguredResolverProtocol,
)

# Configuration
APP_CONFIG = {
    "app": {"name": "My API", "version": "1.0.0"},
    "database": {"url": "postgres://{{db.host}}/{{db.name}}"}
}

RUNTIME_CONTEXT = {
    "db": {"host": "localhost", "name": "mydb"}
}

# Resolve config at startup
_resolver = TemplateResolver()
resolved_config = _resolver.resolve_object(APP_CONFIG, RUNTIME_CONTEXT)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {resolved_config['app']['name']}")
    yield
    print("Shutting down")

app = FastAPI(lifespan=lifespan)

get_resolver = create_resolver_dependency(
    options=ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
)

class ResolveRequest(BaseModel):
    template: str
    context: Dict[str, Any]

@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": resolved_config["app"]["name"],
        "version": resolved_config["app"]["version"]
    }

@app.post("/resolve")
def resolve_template(
    request: ResolveRequest,
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)]
):
    result = resolver.resolve(request.template, request.context)
    return {"original": request.template, "resolved": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Running the Application

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Resolve template
curl -X POST http://localhost:8000/resolve \
  -H "Content-Type: application/json" \
  -d '{"template": "Hello {{name}}!", "context": {"name": "World"}}'
```
