"""
FastAPI Example Application

A minimal FastAPI server demonstrating integration with the server package.
This example shows:
- Server initialization with configuration
- Request state management via middleware
- Health and feature-specific demo routes
- Dependency injection patterns

Run: uvicorn fastapi_app.main:app --reload --port 8080
"""
import copy
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any, Dict, Optional

from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

from logger import logger

# =============================================================================
# Configuration
# =============================================================================

# Mock configuration (in production, load from app-yaml or environment)
CONFIG: Dict[str, Any] = {
    "title": "FastAPI Example Server",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": int(os.getenv("PORT", "8080")),
    "log_level": os.getenv("LOG_LEVEL", "info"),
    "initial_state": {
        "user": None,
        "authenticated": False,
        "permissions": [],
        "request_id": None,
    },
}

# Create logger for this module
log = logger.create("fastapi_app", __file__)


# =============================================================================
# Models
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str


class EchoResponse(BaseModel):
    """Echo endpoint response model."""
    message: str
    user: Optional[str]


class UserResponse(BaseModel):
    """User info response model."""
    user: Optional[str]
    authenticated: bool
    permissions: list


class StateResponse(BaseModel):
    """Request state response model."""
    request_id: Optional[str]
    user: Optional[str]
    authenticated: bool


# =============================================================================
# Lifespan Context Manager
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    log.info("Application starting up", {"title": CONFIG["title"]})

    # Store configuration in app state
    app.state.config = CONFIG
    app.state.initial_state = CONFIG.get("initial_state", {})

    # Simulate resource initialization
    log.info("Resources initialized")

    yield

    # Shutdown
    log.info("Application shutting down")

    # Simulate resource cleanup
    log.info("Resources cleaned up")


# =============================================================================
# Application Factory
# =============================================================================

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Returns a fully configured FastAPI instance.
    """
    app = FastAPI(
        title=CONFIG["title"],
        version=CONFIG["version"],
        lifespan=lifespan,
    )

    # Add request state middleware
    @app.middleware("http")
    async def init_request_state_middleware(request: Request, call_next):
        """Initialize request state from config for each request."""
        initial_state = getattr(request.app.state, "initial_state", {})

        if initial_state:
            # Deep copy to ensure request isolation
            state_copy = copy.deepcopy(initial_state)

            # Generate a unique request ID
            import uuid
            state_copy["request_id"] = str(uuid.uuid4())[:8]

            # Set attributes on request.state
            for key, value in state_copy.items():
                setattr(request.state, key, value)

            log.trace("Request state initialized", {
                "request_id": state_copy["request_id"],
                "path": str(request.url.path),
            })

        response = await call_next(request)
        return response

    return app


# =============================================================================
# Dependencies
# =============================================================================

def get_config(request: Request) -> Dict[str, Any]:
    """Dependency: Get application configuration."""
    return getattr(request.app.state, "config", CONFIG)


def get_request_state(request: Request) -> Dict[str, Any]:
    """Dependency: Get current request state as dict."""
    state = request.state
    return {
        "request_id": getattr(state, "request_id", None),
        "user": getattr(state, "user", None),
        "authenticated": getattr(state, "authenticated", False),
        "permissions": getattr(state, "permissions", []),
    }


def get_user(request: Request) -> Optional[str]:
    """Dependency: Get current user from request state."""
    return getattr(request.state, "user", None)


# Type aliases for dependency injection
Config = Annotated[Dict[str, Any], Depends(get_config)]
RequestState = Annotated[Dict[str, Any], Depends(get_request_state)]
CurrentUser = Annotated[Optional[str], Depends(get_user)]


# =============================================================================
# Create Application Instance
# =============================================================================

app = create_app()


# =============================================================================
# Routes
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint.
    Returns a welcome message.
    """
    return {"message": "Welcome to FastAPI Example Server"}


@app.get("/health", response_model=HealthResponse)
async def health(config: Config):
    """
    Health check endpoint.
    Returns service status and version.
    """
    log.debug("Health check requested")
    return HealthResponse(
        status="ok",
        service=config["title"],
        version=config["version"],
    )


@app.get("/echo/{message}", response_model=EchoResponse)
async def echo(message: str, user: CurrentUser):
    """
    Echo endpoint.
    Returns the message and current user from request state.
    """
    log.info("Echo requested", {"message": message, "user": user})
    return EchoResponse(
        message=message,
        user=user,
    )


@app.get("/me", response_model=UserResponse)
async def me(request: Request):
    """
    Current user endpoint.
    Returns user info from request state.
    """
    state = request.state
    return UserResponse(
        user=getattr(state, "user", None),
        authenticated=getattr(state, "authenticated", False),
        permissions=getattr(state, "permissions", []),
    )


@app.get("/state", response_model=StateResponse)
async def get_state(state: RequestState):
    """
    Request state endpoint.
    Demonstrates dependency injection for state access.
    """
    return StateResponse(
        request_id=state["request_id"],
        user=state["user"],
        authenticated=state["authenticated"],
    )


@app.post("/login")
async def login(request: Request, username: str = "demo_user"):
    """
    Simulated login endpoint.
    Sets user in request state (for demo purposes only).
    Note: In real apps, state changes don't persist between requests.
    """
    # This modifies state only for THIS request
    request.state.user = username
    request.state.authenticated = True
    request.state.permissions = ["read", "write"]

    log.info("User logged in (for this request)", {"user": username})

    return {
        "message": f"Logged in as {username}",
        "note": "State is per-request; next request starts fresh",
    }


@app.get("/config")
async def get_config_endpoint(config: Config):
    """
    Configuration endpoint.
    Returns non-sensitive configuration values.
    """
    return {
        "title": config["title"],
        "version": config["version"],
        "log_level": config["log_level"],
    }


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    log.info("Starting development server", {
        "host": CONFIG["host"],
        "port": CONFIG["port"],
    })

    uvicorn.run(
        "main:app",
        host=CONFIG["host"],
        port=CONFIG["port"],
        reload=True,
        log_level=CONFIG["log_level"],
    )
