from typing import Any, Dict, Optional
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import os

from ..logger import Logger
from ..sdk import create_resolver, create_registry
from ..options import ComputeScope
from ..compute_registry import ComputeRegistry
from ..context_resolver import ContextResolver

def configure_resolver(
    app: FastAPI,
    config: Dict[str, Any],
    registry: Optional[ComputeRegistry] = None,
    state_property: str = "config",
    logger: Optional[Logger] = None
) -> None:
    """
    Configure Runtime Template Resolver for FastAPI application.
    
    Args:
        app: FastAPI application instance
        config: Raw configuration dictionary (usually from AppYaml)
        registry: Compute registry instance
        state_property: Property name to store resolved config in app.state (supports dot notation)
        logger: Logger instance
    """
    _logger = logger or Logger.create("runtime_template_resolver", __file__)
    
    # Store options in app.state for retrieval in depends
    app.state._resolver_options = {
        "config": config,
        "registry": registry,
        "state_property": state_property
    }
    
    # We can't easily add a middleware that modifies lifecycle here because 
    # configure_resolver is usually called INSIDE a lifecycle hook or BEFORE app start.
    # The plan says "Create FastAPI lifespan context manager for STARTUP".
    
    # But usually the user invokes this inside their own lifespan or startup event.
    # The plan says "configure_resolver(app, ...)".
    # And "Lifespan context manager for STARTUP resolution".
    
    # Implementation:
    # 1. Resolve STARTUP config immediately if we act as a setup function.
    # But startup is async.
    # If configure_resolver is synchronous, it can't await resolve.
    # But if called from async lifespan, it can be awaited if async.
    # Plan says: "Logic: Create FastAPI lifespan context manager for STARTUP"
    # Maybe `configure_resolver` returns a lifespan?
    
    # However, integrating with existing app that HAS a lifespan is tricky (lifespan wrapping).
    # Plan Section 7.1 says: "configure_resolver(...) takes config object... Lifespan context manager for STARTUP resolution".
    
    # If this is "server integration", the 02_context_resolver.py IS the lifecycle hook.
    # So `configure_resolver` is a helper called BY the lifecycle hook.
    # As the 02_context_resolver.py is async `onStartup`, we can await there.
    # So `configure_resolver` should probably just setup the RESOLVER instance and perform STARTUP resolution?
    # Yes.
    pass # Code continues below in async logic

async def resolve_startup(
    app: FastAPI,
    config: Dict[str, Any],
    registry: ComputeRegistry,
    state_property: str = "config",
    logger: Optional[Logger] = None
) -> None:
    """Async helper to perform startup resolution"""
    _logger = logger or Logger.create("runtime_template_resolver", __file__)
    
    resolver = create_resolver(registry=registry, logger=_logger)
    
    # Get app config from app.state.config (AppYamlConfig instance decorated by 01_app_yaml)
    server_config = getattr(app.state, "config", None)
    app_config_dict = {}
    if server_config:
        if hasattr(server_config, "get_all"):
            app_config_dict = server_config.get_all()
        elif hasattr(server_config, "to_dict"):
            app_config_dict = server_config.to_dict()
    app_config_dict = app_config_dict or config or {}

    # Build STARTUP context - expose app at top level for {{app.name}} etc.
    startup_context = {
        "env": dict(os.environ),
        "config": config,
        "app": app_config_dict.get("app", {}),
    }
    
    _logger.debug("Resolving configuration (STARTUP scope)...")
    resolved_config = await resolver.resolve_object(
        config,
        context=startup_context,
        scope=ComputeScope.STARTUP
    )
    
    # Store in app.state
    # Handle dot notation for state_property
    _set_nested_attr(app.state, state_property, resolved_config)
    
    # Store resolver/registry for request usage
    app.state._context_resolver = resolver
    app.state._context_registry = registry
    app.state._context_raw_config = config
    app.state._context_state_prop = state_property # Store where we put it

def _set_nested_attr(obj: Any, path: str, value: Any) -> None:
    parts = path.split('.')
    current = obj
    for i, part in enumerate(parts[:-1]):
        if not hasattr(current, part):
             # Ensure intermediate objects exist? 
             # For app.state, we can just set attributes if they don't exist?
             # But app.state attributes are arbitrary.
             # If we want nested objects, we might need to create SimpleNamespace or dicts?
             # FastAPI app.state is generic object.
             # Usually we just set `app.state.resolved_config`.
             # If user passes `resolved.config`, we expect `app.state.resolved` to exist??
             # Or we create it.
             setattr(current, part, type('StateObj', (), {})())
        current = getattr(current, part)
    
    setattr(current, parts[-1], value)

async def get_request_config(request: Request) -> Any:
    """
    Dependency to get resolved configuration for the current request.
    Performs REQUEST scope resolution.
    """
    resolver: ContextResolver = getattr(request.app.state, "_context_resolver", None)
    registry: ComputeRegistry = getattr(request.app.state, "_context_registry", None)
    raw_config: Dict[str, Any] = getattr(request.app.state, "_context_raw_config", {})
    
    if not resolver or not registry:
        # Fallback or error?
        # If STARTUP resolution didn't run, we can't do much.
        raise RuntimeError("Runtime Template Resolver not configured")

    # Get app config from app.state.config (AppYamlConfig instance)
    server_cfg = getattr(request.app.state, "config", None)
    app_cfg_dict = {}
    if server_cfg:
        if hasattr(server_cfg, "get_all"):
            app_cfg_dict = server_cfg.get_all()
        elif hasattr(server_cfg, "to_dict"):
            app_cfg_dict = server_cfg.to_dict()
    app_cfg_dict = app_cfg_dict or raw_config or {}

    # Build REQUEST context - expose app at top level for {{app.name}} etc., and state for request.state
    req_context = {
        "env": dict(os.environ),
        "config": raw_config,
        "app": app_cfg_dict.get("app", {}),
        "state": getattr(request.state, "__dict__", {}) if hasattr(request, "state") else {},
        "request": request,
    }
    
    # Resolve again with REQUEST scope?
    # Wait, if we resolve entire config object every request, that's heavy.
    # Plan says: "REQUEST scope - function runs per-call with request context"
    # Ideally we only resolve parts that are dynamic.
    # But `resolve_object` traverses everything.
    # Optimization: `resolve_object` could cache static parts?
    # Or we rely on `resolve_object` being fast enough?
    # For now, full resolution.
    
    # We resolve the RAW config again?
    # Or we resolve the STARTUP-resolved config?
    # If we resolve Startup-resolved config, we duplicate work?
    # Better to resolve RAW config, but STARTUP functions are cached in registry.
    
    return await resolver.resolve_object(
        raw_config,
        context=req_context,
        scope=ComputeScope.REQUEST
    )
