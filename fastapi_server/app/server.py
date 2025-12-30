import asyncio
import copy
import importlib.util
import os
import signal
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Request

from app.logger import logger

log = logger.create("server", __file__)

# --- Interface Implementation ---

def init(config: Dict[str, Any]) -> FastAPI:
    """Initialize and return native FastAPI instance."""
    log.debug("Initializing FastAPI server", {"title": config.get("title")})

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: Execute registered startup hooks
        startup_hooks = getattr(app.state, "startup_hooks", [])
        config = getattr(app.state, "config", {})

        # Run startup hooks with (server, config)
        log.debug("Executing startup hooks", {"count": len(startup_hooks)})
        for hook in startup_hooks:
            hook_name = getattr(hook, "__name__", "anonymous")
            log.trace("Running startup hook", {"hookName": hook_name})
            if asyncio.iscoroutinefunction(hook):
                await hook(app, config)
            else:
                hook(app, config)
        log.info("Startup hooks completed", {"count": len(startup_hooks)})

        yield

        # Shutdown: Execute registered shutdown hooks
        shutdown_hooks = getattr(app.state, "shutdown_hooks", [])

        # Run shutdown hooks with (server, config)
        log.info("Executing shutdown hooks", {"count": len(shutdown_hooks)})
        for hook in shutdown_hooks:
            hook_name = getattr(hook, "__name__", "anonymous")
            log.trace("Running shutdown hook", {"hookName": hook_name})
            if asyncio.iscoroutinefunction(hook):
                await hook(app, config)
            else:
                hook(app, config)
        log.info("Shutdown hooks completed")

    app = FastAPI(
        title=config.get("title", "API Server"),
        lifespan=lifespan
    )
    log.info("FastAPI server initialized", {"title": config.get("title")})
    return app


async def start(server: FastAPI, config: Dict[str, Any]) -> None:
    """Start server with bootstrap configuration."""
    log.info("Starting server bootstrap sequence", {"title": config.get("title")})
    bootstrap = config.get("bootstrap", {})
    startup_hooks = []
    shutdown_hooks = []

    # Bootstrap: glob and execute env loader modules from directory
    if bootstrap.get("load_env"):
        env_dir = Path(bootstrap["load_env"])
        log.debug("Loading environment modules", {"path": str(env_dir)})
        if env_dir.exists():
            module_files = sorted(env_dir.glob("*.py"))
            log.trace("Found env modules", {"count": len(module_files), "files": [str(f) for f in module_files]})
            for module_path in module_files:
                log.debug("Loading env module", {"module": str(module_path)})
                spec = importlib.util.spec_from_file_location(module_path.stem, str(module_path))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
            log.info("Environment modules loaded", {"count": len(module_files)})
        else:
            log.warn("Environment directory does not exist", {"path": str(env_dir)})

    # Bootstrap: glob and load lifecycle modules from directory
    if bootstrap.get("lifecycle"):
        lifecycle_dir = Path(bootstrap["lifecycle"])
        log.debug("Loading lifecycle modules", {"path": str(lifecycle_dir)})
        if lifecycle_dir.exists():
            module_files = sorted(lifecycle_dir.glob("*.py"))
            log.trace("Found lifecycle modules", {"count": len(module_files), "files": [str(f) for f in module_files]})
            for module_path in module_files:
                log.debug("Loading lifecycle module", {"module": str(module_path)})
                spec = importlib.util.spec_from_file_location(module_path.stem, str(module_path))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "onStartup"):
                        startup_hooks.append(module.onStartup)
                    if hasattr(module, "onShutdown"):
                        shutdown_hooks.append(module.onShutdown)
            log.info("Lifecycle modules loaded", {"count": len(module_files), "startupHooks": len(startup_hooks), "shutdownHooks": len(shutdown_hooks)})
        else:
            log.warn("Lifecycle directory does not exist", {"path": str(lifecycle_dir)})

    # Store hooks and config in app state for use in lifespan
    log.debug("Storing hooks and config in app state")
    server.state.startup_hooks = startup_hooks
    server.state.shutdown_hooks = shutdown_hooks
    server.state.config = config

    # Feature: Initial Request State
    # If config provides 'initial_state', deep clone it to request.state for every request
    initial_state = config.get("initial_state")
    if initial_state:
        log.debug("Configuring initial request state", {"keys": list(initial_state.keys())})
        server.state.initial_state = initial_state

        @server.middleware("http")
        async def init_request_state_middleware(request: Request, call_next):
            # Deepcopy initial state attributes to request.state
            # FastAPI's request.state is a generic object, so we set attributes on it
            state_copy = copy.deepcopy(request.app.state.initial_state)
            if isinstance(state_copy, dict):
                for key, value in state_copy.items():
                    setattr(request.state, key, value)
            log.trace("Request state initialized", {"path": str(request.url.path)})

            response = await call_next(request)
            return response

        log.info("Initial request state feature enabled")

    # Configure Uvicorn
    host = config.get("host", "0.0.0.0")
    port = int(os.getenv("PORT", config.get("port", 8080)))
    log_level = config.get("log_level", "info").lower()

    log.info("Configuring Uvicorn server", {"host": host, "port": port, "log_level": log_level})
    uvicorn_config = uvicorn.Config(
        server,
        host=host,
        port=port,
        log_level=log_level,
    )

    server_instance = uvicorn.Server(uvicorn_config)

    # Handle shutdown signals is built-in to Uvicorn, but we can wrap if needed.
    # Uvicorn handles SIGINT/SIGTERM and triggers lifespan shutdown.

    log.info("Starting HTTP listener", {"host": host, "port": port})
    await server_instance.serve()
    log.info("Server stopped")


async def stop(server: FastAPI, config: Dict[str, Any]) -> None:
    """
    Gracefully stop the server.
    Note: When running with uvicorn.run or Server.serve(),
    stopping is usually handled by signal interruption.
    This method is exposed for programmatic stopping if needed,
    but typically uvicorn handles the loop.
    """
    log.info("Stop requested", {"title": config.get("title")})
    # In a typical uvicorn setup, we don't manually stop the server object
    # from the outside easily unless we have access to the uvicorn.Server instance
    # which is local to `start`.
    # For now, this is a placeholder or could trigger a signal.
    # However, since `start` awaits `serve()`, `stop` might be called from another task.
    log.debug("Stop is a placeholder - uvicorn handles shutdown via signals")
    pass
