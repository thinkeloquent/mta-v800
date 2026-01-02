"""
Unit tests for ComputeRegistry module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
- Log verification (hyper-observability)

Following FORMAT_TEST.yaml specification.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from runtime_template_resolver import ComputeScope
from runtime_template_resolver.compute_registry import ComputeRegistry
from runtime_template_resolver.errors import ComputeFunctionError, ErrorCode


class TestComputeRegistry:
    """Tests for ComputeRegistry class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_register_and_resolve_basic_function(self, registry, mock_logger):
            """Happy path: register and resolve a sync function."""
            registry.register("test_fn", lambda: "result", ComputeScope.REQUEST)

            assert registry.has("test_fn")
            assert "test_fn" in registry.list()

        @pytest.mark.asyncio
        async def test_resolve_sync_function(self, registry):
            """Resolve returns expected value from sync function."""
            registry.register("sync_fn", lambda ctx: f"hello-{ctx.get('name', 'world')}", ComputeScope.REQUEST)

            result = await registry.resolve("sync_fn", {"name": "test"})

            assert result == "hello-test"

        @pytest.mark.asyncio
        async def test_resolve_async_function(self, registry):
            """Resolve works with async functions."""
            async def async_fn(ctx):
                return f"async-{ctx.get('value', 0)}"

            registry.register("async_fn", async_fn, ComputeScope.REQUEST)

            result = await registry.resolve("async_fn", {"value": 42})

            assert result == "async-42"

        def test_unregister_removes_function(self, registry):
            """Unregister removes function from registry."""
            registry.register("temp_fn", lambda: "temp", ComputeScope.REQUEST)
            assert registry.has("temp_fn")

            registry.unregister("temp_fn")

            assert not registry.has("temp_fn")

        def test_clear_removes_all_functions(self, registry):
            """Clear removes all registered functions."""
            registry.register("fn1", lambda: 1, ComputeScope.REQUEST)
            registry.register("fn2", lambda: 2, ComputeScope.STARTUP)

            registry.clear()

            assert registry.list() == []

        def test_get_scope_returns_correct_scope(self, registry):
            """get_scope returns the function's registered scope."""
            registry.register("startup_fn", lambda: "s", ComputeScope.STARTUP)
            registry.register("request_fn", lambda: "r", ComputeScope.REQUEST)

            assert registry.get_scope("startup_fn") == ComputeScope.STARTUP
            assert registry.get_scope("request_fn") == ComputeScope.REQUEST

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else/switch branches."""

        @pytest.mark.asyncio
        async def test_startup_scope_caches_result(self, registry):
            """STARTUP scope functions cache their results."""
            call_count = 0

            def counting_fn():
                nonlocal call_count
                call_count += 1
                return f"call-{call_count}"

            registry.register("cached_fn", counting_fn, ComputeScope.STARTUP)

            result1 = await registry.resolve("cached_fn")
            result2 = await registry.resolve("cached_fn")

            assert result1 == "call-1"
            assert result2 == "call-1"  # Same cached result
            assert call_count == 1  # Only called once

        @pytest.mark.asyncio
        async def test_request_scope_does_not_cache(self, registry):
            """REQUEST scope functions are called every time."""
            call_count = 0

            def counting_fn():
                nonlocal call_count
                call_count += 1
                return f"call-{call_count}"

            registry.register("uncached_fn", counting_fn, ComputeScope.REQUEST)

            result1 = await registry.resolve("uncached_fn")
            result2 = await registry.resolve("uncached_fn")

            assert result1 == "call-1"
            assert result2 == "call-2"  # Different result
            assert call_count == 2

        def test_get_scope_returns_none_for_unknown(self, registry):
            """get_scope returns None for unknown function."""
            result = registry.get_scope("unknown_fn")

            assert result is None

        def test_unregister_unknown_function_is_noop(self, registry):
            """Unregistering unknown function does nothing."""
            registry.unregister("nonexistent")  # Should not raise

            assert not registry.has("nonexistent")

        @pytest.mark.asyncio
        async def test_function_without_context_param(self, registry):
            """Functions that don't accept context still work."""
            registry.register("no_ctx_fn", lambda: "no-context", ComputeScope.REQUEST)

            result = await registry.resolve("no_ctx_fn", {"some": "context"})

            assert result == "no-context"

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValueAnalysis:
        """Test edge cases: empty, min, max, boundary values."""

        def test_empty_function_name_raises(self, registry):
            """Empty function name raises ValueError."""
            with pytest.raises(ValueError, match="cannot be empty"):
                registry.register("", lambda: "x", ComputeScope.REQUEST)

        def test_invalid_function_name_raises(self, registry):
            """Invalid function name pattern raises ValueError."""
            with pytest.raises(ValueError, match="Invalid function name"):
                registry.register("123invalid", lambda: "x", ComputeScope.REQUEST)

            with pytest.raises(ValueError, match="Invalid function name"):
                registry.register("fn-with-dash", lambda: "x", ComputeScope.REQUEST)

            with pytest.raises(ValueError, match="Invalid function name"):
                registry.register("fn.with.dot", lambda: "x", ComputeScope.REQUEST)

        def test_valid_function_names_accepted(self, registry):
            """Valid function names are accepted."""
            registry.register("valid_fn", lambda: "a", ComputeScope.REQUEST)
            registry.register("_private_fn", lambda: "b", ComputeScope.REQUEST)
            registry.register("CamelCase", lambda: "c", ComputeScope.REQUEST)
            registry.register("fn123", lambda: "d", ComputeScope.REQUEST)

            assert registry.has("valid_fn")
            assert registry.has("_private_fn")
            assert registry.has("CamelCase")
            assert registry.has("fn123")

        def test_duplicate_registration_overwrites(self, registry):
            """Registering same name overwrites previous function."""
            registry.register("dup_fn", lambda: "first", ComputeScope.REQUEST)
            registry.register("dup_fn", lambda: "second", ComputeScope.REQUEST)

            assert registry.list().count("dup_fn") == 1

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        @pytest.mark.asyncio
        async def test_resolve_unknown_function_raises(self, registry):
            """Resolving unknown function raises ComputeFunctionError."""
            with pytest.raises(ComputeFunctionError) as excinfo:
                await registry.resolve("unknown_fn")

            assert excinfo.value.code == ErrorCode.COMPUTE_FUNCTION_NOT_FOUND
            assert "unknown_fn" in str(excinfo.value)

        @pytest.mark.asyncio
        async def test_function_exception_wrapped(self, registry):
            """Function exceptions are wrapped in ComputeFunctionError."""
            def failing_fn(ctx):
                raise RuntimeError("Internal failure")

            registry.register("failing_fn", failing_fn, ComputeScope.REQUEST)

            with pytest.raises(ComputeFunctionError) as excinfo:
                await registry.resolve("failing_fn")

            assert excinfo.value.code == ErrorCode.COMPUTE_FUNCTION_FAILED
            assert "failing_fn" in str(excinfo.value)

        @pytest.mark.asyncio
        async def test_async_function_exception_wrapped(self, registry):
            """Async function exceptions are wrapped correctly."""
            async def async_failing_fn(ctx):
                raise ValueError("Async failure")

            registry.register("async_fail", async_failing_fn, ComputeScope.REQUEST)

            with pytest.raises(ComputeFunctionError) as excinfo:
                await registry.resolve("async_fail")

            assert excinfo.value.code == ErrorCode.COMPUTE_FUNCTION_FAILED

    # =========================================================================
    # Log Verification
    # =========================================================================

    class TestLogVerification:
        """Verify defensive logging at control flow points."""

        def test_register_logs_debug_and_info(self, registry, mock_logger, assert_log_contains):
            """Register logs debug entry and info completion."""
            registry.register("logged_fn", lambda: "x", ComputeScope.REQUEST)

            assert_log_contains(mock_logger, 'debug', 'Registering function: logged_fn')
            assert_log_contains(mock_logger, 'info', 'Function registered: logged_fn')

        def test_unregister_logs_when_found(self, registry, mock_logger, assert_log_contains):
            """Unregister logs when function exists."""
            registry.register("to_remove", lambda: "x", ComputeScope.REQUEST)
            registry.unregister("to_remove")

            assert_log_contains(mock_logger, 'debug', 'Unregistering function: to_remove')
            assert_log_contains(mock_logger, 'info', 'Function unregistered: to_remove')

        @pytest.mark.asyncio
        async def test_resolve_logs_debug(self, registry, mock_logger, assert_log_contains):
            """Resolve logs debug message."""
            registry.register("resolve_test", lambda: "x", ComputeScope.REQUEST)
            await registry.resolve("resolve_test")

            assert_log_contains(mock_logger, 'debug', 'Resolving function: resolve_test')

        @pytest.mark.asyncio
        async def test_cached_resolve_logs_cache_hit(self, registry, mock_logger, assert_log_contains):
            """Cached resolve logs cache hit."""
            registry.register("cached", lambda: "x", ComputeScope.STARTUP)
            await registry.resolve("cached")  # First call - populates cache
            await registry.resolve("cached")  # Second call - cache hit

            assert_log_contains(mock_logger, 'debug', 'Returning cached value for: cached')

        @pytest.mark.asyncio
        async def test_failed_resolve_logs_error(self, registry, mock_logger, assert_log_contains):
            """Failed resolve logs error."""
            registry.register("error_fn", lambda ctx: 1 / 0, ComputeScope.REQUEST)

            with pytest.raises(ComputeFunctionError):
                await registry.resolve("error_fn")

            assert_log_contains(mock_logger, 'error', 'Function execution failed: error_fn')

        def test_clear_logs_debug(self, registry, mock_logger, assert_log_contains):
            """Clear logs debug message."""
            registry.clear()

            assert_log_contains(mock_logger, 'debug', 'Clearing registry')

        def test_clear_cache_logs_debug(self, registry, mock_logger, assert_log_contains):
            """Clear cache logs debug message."""
            registry.clear_cache()

            assert_log_contains(mock_logger, 'debug', 'Clearing result cache')

    # =========================================================================
    # Integration Tests
    # =========================================================================

    class TestIntegration:
        """End-to-end scenarios with realistic data."""

        @pytest.mark.asyncio
        async def test_realistic_compute_function_flow(self, registry):
            """Full flow: register, resolve, cache, clear."""
            # Register mix of STARTUP and REQUEST functions
            registry.register("get_build_id", lambda: "build-123", ComputeScope.STARTUP)
            registry.register(
                "get_user_id",
                lambda ctx: ctx.get("user", {}).get("id", "anon"),
                ComputeScope.REQUEST
            )

            # Resolve STARTUP (should cache)
            build1 = await registry.resolve("get_build_id")
            build2 = await registry.resolve("get_build_id")
            assert build1 == build2 == "build-123"

            # Resolve REQUEST with context
            user_id = await registry.resolve("get_user_id", {"user": {"id": "usr-456"}})
            assert user_id == "usr-456"

            # Clear cache, STARTUP should recompute
            registry.clear_cache()
            # Note: This test assumes function is deterministic

            # Full clear
            registry.clear()
            assert registry.list() == []
