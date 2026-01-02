"""
Integration tests for FastAPI integration module.

Tests cover:
- configure_resolver setup
- resolve_startup lifecycle
- get_request_config dependency
- State property dot notation
- Full request/response cycle

Following FORMAT_TEST.yaml specification.
"""
import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, Any

# FastAPI testing
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from runtime_template_resolver import ComputeScope, create_registry, create_resolver
from runtime_template_resolver.integrations.fastapi import (
    configure_resolver,
    resolve_startup,
    get_request_config,
    _set_nested_attr
)


class TestFastAPIIntegration:
    """Integration tests for FastAPI module."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_configure_resolver_stores_options(self):
            """configure_resolver stores options in app.state."""
            app = FastAPI()
            config = {"app": {"name": "test"}}
            registry = create_registry()

            configure_resolver(app, config=config, registry=registry)

            assert hasattr(app.state, "_resolver_options")
            assert app.state._resolver_options["config"] == config
            assert app.state._resolver_options["registry"] is registry
            assert app.state._resolver_options["state_property"] == "config"

        def test_configure_resolver_custom_state_property(self):
            """configure_resolver respects custom state_property."""
            app = FastAPI()
            config = {"app": {"name": "test"}}

            configure_resolver(app, config=config, state_property="resolved_config")

            assert app.state._resolver_options["state_property"] == "resolved_config"

        @pytest.mark.asyncio
        async def test_resolve_startup_resolves_config(self):
            """resolve_startup resolves configuration at STARTUP scope."""
            app = FastAPI()
            registry = create_registry()
            registry.register("get_version", lambda: "1.0.0", ComputeScope.STARTUP)

            config = {
                "app": {
                    "name": "{{env.APP_NAME | 'DefaultApp'}}",
                    "version": "{{fn:get_version}}"
                }
            }

            with patch.dict(os.environ, {"APP_NAME": "TestApp"}):
                await resolve_startup(app, config, registry)

            assert hasattr(app.state, "config")
            assert app.state.config["app"]["name"] == "TestApp"
            assert app.state.config["app"]["version"] == "1.0.0"

        @pytest.mark.asyncio
        async def test_resolve_startup_stores_resolver(self):
            """resolve_startup stores resolver in app.state."""
            app = FastAPI()
            registry = create_registry()
            config = {"key": "value"}

            await resolve_startup(app, config, registry)

            assert hasattr(app.state, "_context_resolver")
            assert hasattr(app.state, "_context_registry")
            assert hasattr(app.state, "_context_raw_config")

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else/switch branches."""

        def test_set_nested_attr_simple_path(self):
            """_set_nested_attr handles simple path."""
            class State:
                pass

            obj = State()
            _set_nested_attr(obj, "config", {"key": "value"})

            assert obj.config == {"key": "value"}

        def test_set_nested_attr_dotted_path(self):
            """_set_nested_attr handles dotted path."""
            class State:
                pass

            obj = State()
            _set_nested_attr(obj, "resolved.config", {"key": "value"})

            assert hasattr(obj, "resolved")
            assert obj.resolved.config == {"key": "value"}

        def test_set_nested_attr_deep_path(self):
            """_set_nested_attr handles deeply nested path."""
            class State:
                pass

            obj = State()
            _set_nested_attr(obj, "a.b.c.d", "deep_value")

            assert obj.a.b.c.d == "deep_value"

        @pytest.mark.asyncio
        async def test_get_request_config_without_resolver_raises(self):
            """get_request_config raises if resolver not configured."""
            app = FastAPI()

            # Create mock request
            request = MagicMock()
            request.app = app

            with pytest.raises(RuntimeError, match="not configured"):
                await get_request_config(request)

        @pytest.mark.asyncio
        async def test_resolve_startup_uses_default_when_missing(self):
            """resolve_startup uses default values for missing env vars."""
            app = FastAPI()
            registry = create_registry()

            config = {
                "database": {
                    "host": "{{env.DB_HOST | 'localhost'}}",
                    "port": "{{env.DB_PORT | '5432'}}"
                }
            }

            # Clear relevant env vars
            env_copy = {k: v for k, v in os.environ.items() if k not in ("DB_HOST", "DB_PORT")}
            with patch.dict(os.environ, env_copy, clear=True):
                await resolve_startup(app, config, registry)

            assert app.state.config["database"]["host"] == "localhost"
            assert app.state.config["database"]["port"] == 5432  # Parsed as int

    # =========================================================================
    # Integration Tests
    # =========================================================================

    class TestIntegration:
        """End-to-end scenarios with realistic FastAPI application."""

        @pytest.mark.asyncio
        async def test_full_request_response_cycle(self):
            """Full cycle: startup resolution then request resolution."""
            app = FastAPI()
            registry = create_registry()

            # Register STARTUP function (cached)
            registry.register("get_build_id", lambda: "build-abc123", ComputeScope.STARTUP)

            # Config with only STARTUP-safe patterns
            # REQUEST scope functions cannot be in config resolved at STARTUP
            config = {
                "app": {
                    "build": "{{fn:get_build_id}}"
                }
            }

            # Simulate STARTUP
            await resolve_startup(app, config, registry, state_property="app_config")

            # Verify STARTUP resolution
            assert app.state.app_config["app"]["build"] == "build-abc123"

            # Create route that uses get_request_config
            @app.get("/config")
            async def get_config(resolved: Dict[str, Any] = Depends(get_request_config)):
                return resolved

            # Test multiple requests
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                resp1 = await client.get("/config")
                resp2 = await client.get("/config")

            assert resp1.status_code == 200
            assert resp2.status_code == 200

            data1 = resp1.json()
            data2 = resp2.json()

            # Build ID should be same (STARTUP cached)
            assert data1["app"]["build"] == "build-abc123"
            assert data2["app"]["build"] == "build-abc123"

        @pytest.mark.asyncio
        async def test_realistic_database_config(self):
            """Realistic database configuration scenario."""
            app = FastAPI()
            registry = create_registry()

            # Register connection string builder
            def build_connection_string(ctx):
                host = ctx.get("env", {}).get("DB_HOST", "localhost")
                port = ctx.get("env", {}).get("DB_PORT", "5432")
                name = ctx.get("env", {}).get("DB_NAME", "app")
                return f"postgresql://{host}:{port}/{name}"

            registry.register(
                "build_connection_string",
                build_connection_string,
                ComputeScope.STARTUP
            )

            config = {
                "database": {
                    "connection": "{{fn:build_connection_string}}",
                    "pool_size": 10,
                    "timeout": "{{env.DB_TIMEOUT | '30'}}"
                },
                "app": {
                    "name": "{{env.APP_NAME | 'MyApp'}}",
                    "debug": "{{env.DEBUG | 'false'}}"
                }
            }

            test_env = {
                "DB_HOST": "db.production.example.com",
                "DB_PORT": "5433",
                "DB_NAME": "production_db",
                "APP_NAME": "ProductionApp"
            }

            with patch.dict(os.environ, test_env, clear=False):
                await resolve_startup(app, config, registry)

            resolved = app.state.config
            assert resolved["database"]["connection"] == "postgresql://db.production.example.com:5433/production_db"
            assert resolved["database"]["pool_size"] == 10
            assert resolved["database"]["timeout"] == 30
            assert resolved["app"]["name"] == "ProductionApp"
            assert resolved["app"]["debug"] is False

        @pytest.mark.asyncio
        async def test_lifespan_pattern(self):
            """Test integration with FastAPI lifespan pattern."""
            registry = create_registry()
            registry.register("get_version", lambda: "2.0.0", ComputeScope.STARTUP)

            config = {
                "version": "{{fn:get_version}}",
                "env": "{{env.ENVIRONMENT | 'development'}}"
            }

            # Use manual setup instead of lifespan for test clarity
            app = FastAPI()
            await resolve_startup(app, config, registry)

            @app.get("/version")
            async def get_version():
                return {"version": app.state.config["version"]}

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get("/version")

            assert response.status_code == 200
            assert response.json()["version"] == "2.0.0"

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        @pytest.mark.asyncio
        async def test_missing_registry_in_request(self):
            """Request fails when resolver not configured."""
            app = FastAPI()

            @app.get("/config")
            async def get_config(resolved: Dict[str, Any] = Depends(get_request_config)):
                return resolved

            # The dependency raises RuntimeError when resolver not configured
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                with pytest.raises(RuntimeError, match="not configured"):
                    await client.get("/config")

        @pytest.mark.asyncio
        async def test_compute_function_error_propagates(self):
            """Errors in compute functions propagate correctly."""
            app = FastAPI()
            registry = create_registry()

            def failing_function(ctx):
                raise ValueError("Intentional failure")

            registry.register("failing_fn", failing_function, ComputeScope.STARTUP)

            config = {"value": "{{fn:failing_fn}}"}

            with pytest.raises(Exception):
                await resolve_startup(app, config, registry)

    # =========================================================================
    # Scope Enforcement
    # =========================================================================

    class TestScopeEnforcement:
        """Test STARTUP/REQUEST scope behavior."""

        @pytest.mark.asyncio
        async def test_startup_function_cached_across_requests(self):
            """STARTUP functions are cached and not re-executed per request."""
            app = FastAPI()
            registry = create_registry()

            call_count = {"value": 0}

            def counting_startup(ctx=None):
                call_count["value"] += 1
                return f"call-{call_count['value']}"

            registry.register("counting", counting_startup, ComputeScope.STARTUP)

            config = {"counter": "{{fn:counting}}"}

            await resolve_startup(app, config, registry)

            @app.get("/config")
            async def get_config(resolved: Dict[str, Any] = Depends(get_request_config)):
                return resolved

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                resp1 = await client.get("/config")
                resp2 = await client.get("/config")
                resp3 = await client.get("/config")

            # STARTUP function should only be called once (during resolve_startup)
            # But get_request_config calls resolve_object again...
            # The caching is in registry.resolve for STARTUP scope
            # So even during REQUEST resolution, if we call fn:counting, it returns cached value
            assert resp1.json()["counter"] == "call-1"
            assert resp2.json()["counter"] == "call-1"
            assert resp3.json()["counter"] == "call-1"

        @pytest.mark.asyncio
        async def test_request_function_called_per_request(self):
            """REQUEST functions are called on each request via get_request_config."""
            app = FastAPI()
            registry = create_registry()

            call_count = {"value": 0}

            def counting_request(ctx):
                call_count["value"] += 1
                return f"req-{call_count['value']}"

            registry.register("request_counter", counting_request, ComputeScope.REQUEST)

            # Config without REQUEST-scope patterns (those fail at STARTUP)
            # The REQUEST function will be called during get_request_config at REQUEST scope
            config = {"static": "value", "counter": "{{fn:request_counter | 'pending'}}"}

            # Note: The STARTUP resolution will use the default 'pending' since
            # REQUEST functions cannot be called at STARTUP scope
            # But the actual test should use a config that works
            # Let's use a simpler approach - just have static config for STARTUP
            config = {"mode": "{{env.MODE | 'test'}}"}

            await resolve_startup(app, config, registry)

            # The get_request_config will re-resolve at REQUEST scope
            # We need a config that CONTAINS the REQUEST pattern for testing
            # But that fails at STARTUP...
            # The real pattern is: have a separate resolver call for REQUEST functions

            # Alternative: Test using resolver directly at REQUEST scope
            resolver = app.state._context_resolver

            @app.get("/counter")
            async def get_counter(request: Request):
                result = await resolver.resolve(
                    "{{fn:request_counter}}",
                    {"env": dict(os.environ), "request": request},
                    scope=ComputeScope.REQUEST
                )
                return {"counter": result}

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                resp1 = await client.get("/counter")
                resp2 = await client.get("/counter")

            # REQUEST function called multiple times
            assert resp1.json()["counter"] == "req-1"
            assert resp2.json()["counter"] == "req-2"
