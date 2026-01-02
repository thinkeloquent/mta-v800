import os
import uuid
from datetime import datetime
from fastapi import FastAPI

try:
    from runtime_template_resolver import create_registry, ComputeScope
    from runtime_template_resolver.integrations.fastapi import resolve_startup
    HAS_RESOLVER = True
except ImportError:
    HAS_RESOLVER = False


def register_compute_functions(registry):
    """Register compute functions for template resolution."""

    # ==========================================================================
    # STARTUP Scope - Run once at startup, cached
    # ==========================================================================

    # Echo for testing
    registry.register("echo", lambda ctx: "echo", ComputeScope.STARTUP)

    # Build info from environment
    registry.register("get_build_id", lambda ctx: ctx.get("env", {}).get("BUILD_ID", "dev-local"), ComputeScope.STARTUP)
    registry.register("get_build_version", lambda ctx: ctx.get("env", {}).get("BUILD_VERSION", "0.0.0"), ComputeScope.STARTUP)
    registry.register("get_git_commit", lambda ctx: ctx.get("env", {}).get("GIT_COMMIT", "unknown"), ComputeScope.STARTUP)

    # Service info
    registry.register("get_service_name", lambda ctx: ctx.get("config", {}).get("app", {}).get("name", "mta-server"), ComputeScope.STARTUP)
    registry.register("get_service_version", lambda ctx: ctx.get("config", {}).get("app", {}).get("version", "0.0.0"), ComputeScope.STARTUP)

    # ==========================================================================
    # REQUEST Scope - Run per request with request context
    # ==========================================================================

    # Request ID - from header or generate
    def compute_request_id(ctx):
        request = ctx.get("request")
        if request:
            request_id = request.headers.get("x-request-id")
            if request_id:
                return request_id
        return str(uuid.uuid4())
    registry.register("compute_request_id", compute_request_id, ComputeScope.REQUEST)

    # Gemini token - from header or env
    def compute_localhost_test_case_001_token(ctx):
        request = ctx.get("request")
        if request:
            token = request.headers.get("x-gemini-token")
            if token:
                return token
        return ctx.get("env", {}).get("GEMINI_API_KEY", "")
    registry.register("compute_localhost_test_case_001_token", compute_localhost_test_case_001_token, ComputeScope.REQUEST)

    # Test case 002 - Authorization from jira provider
    def compute_test_case_002(ctx):
        request = ctx.get("request")
        if request:
            token = request.headers.get("x-jira-token")
            if token:
                return f"Bearer {token}"
        api_token = ctx.get("env", {}).get("JIRA_API_TOKEN", "")
        if api_token:
            return f"Bearer {api_token}"
        return ""
    registry.register("test_case_002", compute_test_case_002, ComputeScope.REQUEST)

    # Test case 002_1 - X-Auth header
    def compute_test_case_002_1(ctx):
        request = ctx.get("request")
        if request:
            token = request.headers.get("x-auth")
            if token:
                return token
        return ctx.get("env", {}).get("JIRA_API_TOKEN", "")
    registry.register("test_case_002_1", compute_test_case_002_1, ComputeScope.REQUEST)

    # Tenant ID - from header or query param
    def compute_tenant_id(ctx):
        request = ctx.get("request")
        if request:
            tenant_id = request.headers.get("x-tenant-id")
            if tenant_id:
                return tenant_id
            tenant_id = request.query_params.get("tenant_id")
            if tenant_id:
                return tenant_id
        return "default"
    registry.register("compute_tenant_id", compute_tenant_id, ComputeScope.REQUEST)

    # User agent with app info
    def compute_user_agent(ctx):
        app_name = ctx.get("config", {}).get("app", {}).get("name", "MTA-Server")
        app_version = ctx.get("config", {}).get("app", {}).get("version", "0.0.0")
        base_ua = f"{app_name}/{app_version}"
        request = ctx.get("request")
        if request:
            client_ua = request.headers.get("user-agent")
            if client_ua:
                return f"{base_ua} (via {client_ua})"
        return base_ua
    registry.register("compute_user_agent", compute_user_agent, ComputeScope.REQUEST)


async def onStartup(app: FastAPI, config: dict):
    """Initialize Runtime Template Resolver on startup."""
    if not HAS_RESOLVER:
        print("Warning: runtime_template_resolver not installed. Context resolver skipping.")
        return

    print("Initializing Runtime Template Resolver...")

    # Get config from app.state (set by 01_app_yaml)
    app_config = getattr(app.state, "config", None)
    if not app_config:
        print("Warning: app.state.config not found. Context resolver skipping.")
        return

    # Get raw config dictionary
    if hasattr(app_config, "get_all"):
        raw_config = app_config.get_all()
    elif hasattr(app_config, "to_dict"):
        raw_config = app_config.to_dict()
    else:
        raw_config = {}

    registry = create_registry()
    register_compute_functions(registry)

    # Resolve STARTUP config and store in app.state.resolved_config
    await resolve_startup(
        app=app,
        config=raw_config,
        registry=registry,
        state_property="resolved_config"
    )

    print(f"Runtime Template Resolver initialized. Registered functions: {registry.list()}")
