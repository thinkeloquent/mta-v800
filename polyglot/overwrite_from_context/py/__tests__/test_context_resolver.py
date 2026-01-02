"""
Unit tests for ContextResolver module.

Tests cover:
- Template pattern resolution
- Compute pattern resolution
- Object resolution (recursive)
- Scope enforcement
- Default value handling

Following FORMAT_TEST.yaml specification.
"""
import pytest
from unittest.mock import AsyncMock

from runtime_template_resolver import ComputeScope
from runtime_template_resolver.context_resolver import ContextResolver
from runtime_template_resolver.compute_registry import ComputeRegistry
from runtime_template_resolver.options import ResolverOptions, MissingStrategy
from runtime_template_resolver.errors import (
    ComputeFunctionError,
    RecursionLimitError,
    ScopeViolationError,
    SecurityError,
    ErrorCode
)


class TestContextResolver:
    """Tests for ContextResolver class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_is_compute_pattern_true(self, resolver):
            """Correctly identifies compute pattern."""
            assert resolver.is_compute_pattern("{{fn:my_function}}")
            assert resolver.is_compute_pattern("{{fn:get_value | 'default'}}")

        def test_is_compute_pattern_false(self, resolver):
            """Correctly rejects non-compute patterns."""
            assert not resolver.is_compute_pattern("{{variable}}")
            assert not resolver.is_compute_pattern("plain text")
            assert not resolver.is_compute_pattern("{{env.HOST}}")

        @pytest.mark.asyncio
        async def test_resolve_template_pattern(self, resolver):
            """Resolves template pattern from context."""
            context = {"env": {"HOST": "localhost"}}

            result = await resolver.resolve("{{env.HOST}}", context)

            assert result == "localhost"

        @pytest.mark.asyncio
        async def test_resolve_literal_string(self, resolver):
            """Non-pattern strings are returned as-is."""
            context = {}

            result = await resolver.resolve("plain text", context)

            assert result == "plain text"

        @pytest.mark.asyncio
        async def test_resolve_non_string_passthrough(self, resolver):
            """Non-string values pass through unchanged."""
            context = {}

            assert await resolver.resolve(42, context) == 42
            assert await resolver.resolve(True, context) is True
            assert await resolver.resolve(None, context) is None
            assert await resolver.resolve([1, 2, 3], context) == [1, 2, 3]

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else/switch branches."""

        @pytest.mark.asyncio
        async def test_template_with_default_when_missing(self, resolver):
            """Template uses default when value is missing."""
            context = {}

            result = await resolver.resolve("{{missing.value | 'default_val'}}", context)

            assert result == "default_val"

        @pytest.mark.asyncio
        async def test_template_without_default_when_missing(self, resolver):
            """Template returns original when missing and no default (IGNORE strategy)."""
            options = ResolverOptions(missing_strategy=MissingStrategy.IGNORE)
            registry = ComputeRegistry()
            resolver = ContextResolver(registry=registry, options=options)

            context = {}
            result = await resolver.resolve("{{missing.value}}", context)

            assert result == "{{missing.value}}"

        @pytest.mark.asyncio
        async def test_compute_pattern_resolves_function(self, registry, resolver):
            """Compute pattern calls registered function."""
            registry.register("get_value", lambda ctx: "computed", ComputeScope.REQUEST)

            result = await resolver.resolve("{{fn:get_value}}", {})

            assert result == "computed"

        @pytest.mark.asyncio
        async def test_compute_with_default_on_missing(self, resolver):
            """Compute uses default when function missing."""
            result = await resolver.resolve("{{fn:missing_fn | 'fallback'}}", {})

            assert result == "fallback"

        @pytest.mark.asyncio
        async def test_compute_with_default_on_error(self, registry, resolver):
            """Compute uses default when function fails."""
            registry.register("failing_fn", lambda ctx: 1 / 0, ComputeScope.REQUEST)

            result = await resolver.resolve("{{fn:failing_fn | 'error_fallback'}}", {})

            assert result == "error_fallback"

    # =========================================================================
    # Object Resolution
    # =========================================================================

    class TestObjectResolution:
        """Test resolve_object for nested structures."""

        @pytest.mark.asyncio
        async def test_resolve_dict(self, resolver):
            """Resolves dictionary values."""
            context = {"env": {"HOST": "db.example.com", "PORT": "5432"}}
            obj = {
                "host": "{{env.HOST}}",
                "port": "{{env.PORT}}",
                "name": "static_value"
            }

            result = await resolver.resolve_object(obj, context)

            assert result["host"] == "db.example.com"
            assert result["port"] == "5432"
            assert result["name"] == "static_value"

        @pytest.mark.asyncio
        async def test_resolve_nested_dict(self, resolver):
            """Resolves deeply nested dictionaries."""
            context = {"config": {"db": {"host": "localhost"}}}
            obj = {
                "level1": {
                    "level2": {
                        "value": "{{config.db.host}}"
                    }
                }
            }

            result = await resolver.resolve_object(obj, context)

            assert result["level1"]["level2"]["value"] == "localhost"

        @pytest.mark.asyncio
        async def test_resolve_list(self, resolver):
            """Resolves list elements."""
            context = {"items": {"a": "A", "b": "B"}}
            obj = ["{{items.a}}", "{{items.b}}", "static"]

            result = await resolver.resolve_object(obj, context)

            assert result == ["A", "B", "static"]

        @pytest.mark.asyncio
        async def test_resolve_mixed_structure(self, registry, resolver):
            """Resolves mixed dict/list structures with compute."""
            registry.register("get_id", lambda ctx: "id-123", ComputeScope.REQUEST)

            context = {"env": {"MODE": "production"}}
            obj = {
                "mode": "{{env.MODE}}",
                "id": "{{fn:get_id}}",
                "items": [
                    {"name": "item1"},
                    {"value": "{{env.MODE}}"}
                ]
            }

            result = await resolver.resolve_object(obj, context)

            assert result["mode"] == "production"
            assert result["id"] == "id-123"
            assert result["items"][1]["value"] == "production"

        @pytest.mark.asyncio
        async def test_preserves_non_string_values(self, resolver):
            """Non-string values preserved unchanged."""
            obj = {
                "number": 42,
                "boolean": True,
                "null": None,
                "list": [1, 2, 3]
            }

            result = await resolver.resolve_object(obj, {})

            assert result["number"] == 42
            assert result["boolean"] is True
            assert result["null"] is None
            assert result["list"] == [1, 2, 3]

    # =========================================================================
    # Scope Enforcement
    # =========================================================================

    class TestScopeEnforcement:
        """Test STARTUP/REQUEST scope enforcement."""

        @pytest.mark.asyncio
        async def test_startup_function_at_startup_scope(self, registry, resolver):
            """STARTUP function callable at STARTUP scope."""
            registry.register("startup_fn", lambda: "startup", ComputeScope.STARTUP)

            result = await resolver.resolve(
                "{{fn:startup_fn}}",
                {},
                scope=ComputeScope.STARTUP
            )

            assert result == "startup"

        @pytest.mark.asyncio
        async def test_request_function_blocked_at_startup_scope(self, registry, resolver):
            """REQUEST function blocked at STARTUP scope."""
            registry.register("request_fn", lambda ctx: "request", ComputeScope.REQUEST)

            with pytest.raises(ScopeViolationError) as excinfo:
                await resolver.resolve(
                    "{{fn:request_fn}}",
                    {},
                    scope=ComputeScope.STARTUP
                )

            assert excinfo.value.code == ErrorCode.SCOPE_VIOLATION

        @pytest.mark.asyncio
        async def test_both_scopes_at_request_scope(self, registry, resolver):
            """Both STARTUP and REQUEST callable at REQUEST scope."""
            registry.register("startup_fn", lambda: "s", ComputeScope.STARTUP)
            registry.register("request_fn", lambda ctx: "r", ComputeScope.REQUEST)

            s_result = await resolver.resolve(
                "{{fn:startup_fn}}",
                {},
                scope=ComputeScope.REQUEST
            )
            r_result = await resolver.resolve(
                "{{fn:request_fn}}",
                {},
                scope=ComputeScope.REQUEST
            )

            assert s_result == "s"
            assert r_result == "r"

    # =========================================================================
    # Recursion Protection
    # =========================================================================

    class TestRecursionProtection:
        """Test recursion depth limits."""

        @pytest.mark.asyncio
        async def test_max_depth_exceeded_raises(self, registry):
            """Exceeding max depth raises RecursionLimitError."""
            options = ResolverOptions(max_depth=5)
            resolver = ContextResolver(registry=registry, options=options)

            with pytest.raises(RecursionLimitError) as excinfo:
                await resolver.resolve("{{test}}", {}, depth=10)

            assert excinfo.value.code == ErrorCode.RECURSION_LIMIT

        @pytest.mark.asyncio
        async def test_deeply_nested_object_within_limit(self, registry):
            """Deeply nested object within limit succeeds."""
            options = ResolverOptions(max_depth=20)
            resolver = ContextResolver(registry=registry, options=options)

            # Create nested structure within limit
            obj = {"l1": {"l2": {"l3": {"l4": {"value": "{{env.X | 'deep'}}"}}}}}

            result = await resolver.resolve_object(obj, {})

            assert result["l1"]["l2"]["l3"]["l4"]["value"] == "deep"

    # =========================================================================
    # Default Value Parsing
    # =========================================================================

    class TestDefaultValueParsing:
        """Test type inference for default values."""

        @pytest.mark.asyncio
        async def test_default_boolean_true(self, resolver):
            """Default 'true' parsed as boolean True."""
            result = await resolver.resolve("{{missing | 'true'}}", {})
            assert result is True

        @pytest.mark.asyncio
        async def test_default_boolean_false(self, resolver):
            """Default 'false' parsed as boolean False."""
            result = await resolver.resolve("{{missing | 'false'}}", {})
            assert result is False

        @pytest.mark.asyncio
        async def test_default_integer(self, resolver):
            """Default numeric string parsed as integer."""
            result = await resolver.resolve("{{missing | '42'}}", {})
            assert result == 42
            assert isinstance(result, int)

        @pytest.mark.asyncio
        async def test_default_float(self, resolver):
            """Default float string parsed as float."""
            result = await resolver.resolve("{{missing | '3.14'}}", {})
            assert result == 3.14
            assert isinstance(result, float)

        @pytest.mark.asyncio
        async def test_default_string(self, resolver):
            """Default regular string stays string."""
            result = await resolver.resolve("{{missing | 'hello'}}", {})
            assert result == "hello"
            assert isinstance(result, str)

    # =========================================================================
    # Security Integration
    # =========================================================================

    class TestSecurityIntegration:
        """Test security validation in resolution."""

        @pytest.mark.asyncio
        async def test_blocked_path_raises_security_error(self, resolver):
            """Blocked paths raise SecurityError."""
            with pytest.raises(SecurityError):
                await resolver.resolve("{{obj.__proto__}}", {})

        @pytest.mark.asyncio
        async def test_underscore_path_blocked(self, resolver):
            """Underscore prefix paths blocked."""
            with pytest.raises(SecurityError):
                await resolver.resolve("{{_private.value}}", {})

    # =========================================================================
    # Batch Resolution
    # =========================================================================

    class TestBatchResolution:
        """Test resolve_many for multiple expressions."""

        @pytest.mark.asyncio
        async def test_resolve_many_expressions(self, registry, resolver):
            """Resolves multiple expressions in order."""
            registry.register("get_id", lambda ctx: "ID", ComputeScope.REQUEST)

            context = {"env": {"A": "a", "B": "b"}}
            expressions = ["{{env.A}}", "{{env.B}}", "{{fn:get_id}}", "literal"]

            results = await resolver.resolve_many(expressions, context)

            assert results == ["a", "b", "ID", "literal"]

        @pytest.mark.asyncio
        async def test_resolve_many_empty_list(self, resolver):
            """Resolves empty list returns empty list."""
            results = await resolver.resolve_many([], {})

            assert results == []

    # =========================================================================
    # Integration Tests
    # =========================================================================

    class TestIntegration:
        """End-to-end scenarios with realistic data."""

        @pytest.mark.asyncio
        async def test_realistic_config_resolution(self, registry):
            """Full config resolution scenario."""
            # Register compute functions
            registry.register(
                "get_connection_string",
                lambda ctx: f"postgresql://{ctx['env'].get('DB_HOST', 'localhost')}:5432/app",
                ComputeScope.STARTUP
            )
            registry.register(
                "get_request_id",
                lambda ctx: ctx.get("request", {}).get("id", "unknown"),
                ComputeScope.REQUEST
            )

            resolver = ContextResolver(registry=registry)

            config = {
                "database": {
                    "connection": "{{fn:get_connection_string}}",
                    "pool_size": 10
                },
                "app": {
                    "name": "{{env.APP_NAME | 'MyApp'}}",
                    "debug": "{{env.DEBUG | 'false'}}"
                },
                "request": {
                    "id": "{{fn:get_request_id}}"
                }
            }

            context = {
                "env": {"DB_HOST": "db.prod.example.com", "APP_NAME": "ProductionApp"},
                "request": {"id": "req-12345"}
            }

            result = await resolver.resolve_object(config, context, scope=ComputeScope.REQUEST)

            assert result["database"]["connection"] == "postgresql://db.prod.example.com:5432/app"
            assert result["database"]["pool_size"] == 10
            assert result["app"]["name"] == "ProductionApp"
            assert result["app"]["debug"] is False
            assert result["request"]["id"] == "req-12345"
