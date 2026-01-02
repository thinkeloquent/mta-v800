from fastapi import FastAPI
from runtime_template_resolver import create_registry, ComputeScope, resolve_startup
from runtime_template_resolver.integrations.fastapi import configure_resolver

# We can register compute functions here
def register_compute_functions(registry):
    # Example: Register a function to get request ID (if using request scope)
    # registry.register("get_request_id", lambda ctx: ctx.get("request").state.request_id, ComputeScope.REQUEST)
    
    # Generic echo for testing
    registry.register("echo", lambda ctx: "echo", ComputeScope.STARTUP)
    pass

async def onStartup(app: FastAPI, config: dict):
    print("Initializing Runtime Template Resolver...")
    
    # Get config from app.state (set by 01_app_yaml)
    # app.state.config is AppYamlConfig instance
    # We need the raw dict to resolve.
    # Assuming AppYamlConfig has .get_config() or we can just access internal dict if we know structure.
    # For now, let's assume we can get it.
    # If app.state.config is the singleton instance.
    
    app_config = getattr(app.state, "config", None)
    if not app_config:
        print("Warning: app.state.config not found. Context resolver skipping.")
        return

    # Assuming app_config is the AppYamlConfig instance.
    # We need to get the raw config dictionary.
    # We try typical methods: to_dict(), get_config(), or just casting?
    # Let's assume to_dict() for now.
    raw_config = app_config.to_dict() if hasattr(app_config, "to_dict") else {}
    
    registry = create_registry()
    register_compute_functions(registry)
    
    # Resolve STARTUP config and store in app.state.resolved_config
    await resolve_startup(
        app=app,
        config=raw_config,
        registry=registry,
        state_property="resolved_config" 
    )
    
    print("Runtime Template Resolver initialized. Resolved config available at app.state.resolved_config")
