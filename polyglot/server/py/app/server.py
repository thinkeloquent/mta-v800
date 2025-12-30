import copy
import importlib.util
import os
import signal
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Request


# --- Interface Implementation ---

def init(config: Dict[str, Any]) -> FastAPI:
    """Initialize and return native FastAPI instance."""
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: Execute registered startup hooks
        startup_hooks = getattr(app.state, "startup_hooks", [])
        config = getattr(app.state, "config", {})
        
        # Run startup hooks with (server, config)
        for hook in startup_hooks:
            if asyncio.iscoroutinefunction(hook):
                await hook(app, config)
            else:
                hook(app, config)
                
        yield
        
        # Shutdown: Execute registered shutdown hooks
        shutdown_hooks = getattr(app.state, "shutdown_hooks", [])
        
        # Run shutdown hooks with (server, config)
        for hook in shutdown_hooks:
            if asyncio.iscoroutinefunction(hook):
                await hook(app, config)
            else:
                hook(app, config)

    app = FastAPI(
        title=config.get("title", "API Server"),
        lifespan=lifespan
    )
    return app


async def start(server: FastAPI, config: Dict[str, Any]) -> None:
    """Start server with bootstrap configuration."""
    bootstrap = config.get("bootstrap", {})
    startup_hooks = []
    shutdown_hooks = []

    # Bootstrap: glob and execute env loader modules from directory
    if bootstrap.get("load_env"):
        env_dir = Path(bootstrap["load_env"])
        if env_dir.exists():
            for module_path in sorted(env_dir.glob("*.py")):
                spec = importlib.util.spec_from_file_location(module_path.stem, str(module_path))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

    # Bootstrap: glob and load lifecycle modules from directory
    if bootstrap.get("lifecycle"):
        lifecycle_dir = Path(bootstrap["lifecycle"])
        if lifecycle_dir.exists():
            for module_path in sorted(lifecycle_dir.glob("*.py")):
                spec = importlib.util.spec_from_file_location(module_path.stem, str(module_path))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "onStartup"):
                        startup_hooks.append(module.onStartup)
                    if hasattr(module, "onShutdown"):
                        shutdown_hooks.append(module.onShutdown)

    # Store hooks and config in app state for use in lifespan
    server.state.startup_hooks = startup_hooks
    server.state.shutdown_hooks = shutdown_hooks
    server.state.config = config

    # Feature: Initial Request State
    # If config provides 'initial_state', deep clone it to request.state for every request
    initial_state = config.get("initial_state")
    if initial_state:
        server.state.initial_state = initial_state
        
        @server.middleware("http")
        async def init_request_state_middleware(request: Request, call_next):
            # Deepcopy initial state attributes to request.state
            # FastAPI's request.state is a generic object, so we set attributes on it
            state_copy = copy.deepcopy(request.app.state.initial_state)
            if isinstance(state_copy, dict):
                for key, value in state_copy.items():
                    setattr(request.state, key, value)
            
            response = await call_next(request)
            return response

    # Configure Uvicorn
    uvicorn_config = uvicorn.Config(
        server,
        host=config.get("host", "0.0.0.0"),
        port=int(os.getenv("PORT", config.get("port", 8080))),
        log_level=config.get("log_level", "info").lower(),
    )
    
    server_instance = uvicorn.Server(uvicorn_config)
    
    # Handle shutdown signals is built-in to Uvicorn, but we can wrap if needed.
    # Uvicorn handles SIGINT/SIGTERM and triggers lifespan shutdown.
    
    await server_instance.serve()


async def stop(server: FastAPI, config: Dict[str, Any]) -> None:
    """
    Gracefully stop the server. 
    Note: When running with uvicorn.run or Server.serve(), 
    stopping is usually handled by signal interruption.
    This method is exposed for programmatic stopping if needed,
    but typically uvicorn handles the loop.
    """
    # In a typical uvicorn setup, we don't manually stop the server object 
    # from the outside easily unless we have access to the uvicorn.Server instance 
    # which is local to `start`. 
    # For now, this is a placeholder or could trigger a signal.
    # However, since `start` awaits `serve()`, `stop` might be called from another task.
    pass
