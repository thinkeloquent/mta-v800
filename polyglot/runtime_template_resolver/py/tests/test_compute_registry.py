"""Tests for ComputeRegistry module."""

import pytest
from runtime_template_resolver import (
    ComputeRegistry,
    ComputeScope,
    ComputeFunctionError,
)


class TestComputeRegistryBasics:
    """Basic registration and resolution tests."""

    def test_register_and_resolve_simple_function(self):
        """Test registering and resolving a simple function."""
        registry = ComputeRegistry()
        registry.register("get_value", lambda: 42)
        assert registry.resolve("get_value") == 42

    def test_resolve_with_context(self):
        """Test resolving a function that uses context."""
        registry = ComputeRegistry()
        registry.register("get_host", lambda ctx: ctx.get("HOST", "localhost"))
        assert registry.resolve("get_host", {"HOST": "prod.example.com"}) == "prod.example.com"

    def test_resolve_with_context_default(self):
        """Test resolving with context using default value."""
        registry = ComputeRegistry()
        registry.register("get_host", lambda ctx: ctx.get("HOST", "localhost"))
        assert registry.resolve("get_host", {}) == "localhost"

    def test_resolve_function_without_context_arg(self):
        """Test resolving a function that doesn't accept context."""
        registry = ComputeRegistry()
        registry.register("get_constant", lambda: "constant_value")
        # Should work even when context is passed
        assert registry.resolve("get_constant", {"unused": "data"}) == "constant_value"

    def test_resolve_returns_various_types(self):
        """Test that resolve can return various types."""
        registry = ComputeRegistry()

        registry.register("get_int", lambda: 42)
        registry.register("get_float", lambda: 3.14)
        registry.register("get_dict", lambda: {"key": "value"})
        registry.register("get_list", lambda: [1, 2, 3])
        registry.register("get_bool", lambda: True)
        registry.register("get_none", lambda: None)

        assert registry.resolve("get_int") == 42
        assert registry.resolve("get_float") == 3.14
        assert registry.resolve("get_dict") == {"key": "value"}
        assert registry.resolve("get_list") == [1, 2, 3]
        assert registry.resolve("get_bool") is True
        assert registry.resolve("get_none") is None


class TestComputeRegistryErrors:
    """Error handling tests."""

    def test_resolve_unknown_function(self):
        """Test that resolving unknown function raises error."""
        registry = ComputeRegistry()
        with pytest.raises(ComputeFunctionError, match="Unknown compute function"):
            registry.resolve("unknown")

    def test_duplicate_registration_raises_error(self):
        """Test that duplicate registration raises error."""
        registry = ComputeRegistry()
        registry.register("fn", lambda: 1)
        with pytest.raises(ValueError, match="already registered"):
            registry.register("fn", lambda: 2)

    def test_invalid_empty_function_name(self):
        """Test that empty function name raises error."""
        registry = ComputeRegistry()
        with pytest.raises(ValueError, match="Invalid function name"):
            registry.register("", lambda: 1)

    def test_invalid_function_name_with_hyphen(self):
        """Test that function name with hyphen raises error."""
        registry = ComputeRegistry()
        with pytest.raises(ValueError, match="Invalid function name"):
            registry.register("invalid-name", lambda: 1)

    def test_invalid_function_name_starting_with_number(self):
        """Test that function name starting with number raises error."""
        registry = ComputeRegistry()
        with pytest.raises(ValueError, match="Invalid function name"):
            registry.register("1invalid", lambda: 1)

    def test_function_execution_error(self):
        """Test that function execution error is wrapped."""
        registry = ComputeRegistry()
        registry.register("failing_fn", lambda: 1/0)
        with pytest.raises(ComputeFunctionError, match="Error executing"):
            registry.resolve("failing_fn")


class TestComputeRegistryValidNames:
    """Test valid function name patterns."""

    def test_valid_name_with_underscore(self):
        """Test that underscore in function name is valid."""
        registry = ComputeRegistry()
        registry.register("get_value", lambda: 1)
        assert registry.has("get_value")

    def test_valid_name_starting_with_underscore(self):
        """Test that function name starting with underscore is valid."""
        registry = ComputeRegistry()
        registry.register("_private_fn", lambda: 1)
        assert registry.has("_private_fn")

    def test_valid_name_with_numbers(self):
        """Test that function name with numbers is valid."""
        registry = ComputeRegistry()
        registry.register("get_v2", lambda: 2)
        assert registry.has("get_v2")


class TestComputeRegistryMethods:
    """Test registry utility methods."""

    def test_has_returns_true_for_registered(self):
        """Test has() returns True for registered functions."""
        registry = ComputeRegistry()
        registry.register("exists", lambda: 1)
        assert registry.has("exists") is True

    def test_has_returns_false_for_missing(self):
        """Test has() returns False for missing functions."""
        registry = ComputeRegistry()
        assert registry.has("missing") is False

    def test_list_returns_all_function_names(self):
        """Test list() returns all registered function names."""
        registry = ComputeRegistry()
        registry.register("fn1", lambda: 1)
        registry.register("fn2", lambda: 2)
        registry.register("fn3", lambda: 3)
        assert set(registry.list()) == {"fn1", "fn2", "fn3"}

    def test_list_returns_empty_list_when_empty(self):
        """Test list() returns empty list when no functions registered."""
        registry = ComputeRegistry()
        assert registry.list() == []

    def test_get_scope_returns_correct_scope(self):
        """Test get_scope() returns correct scope."""
        registry = ComputeRegistry()
        registry.register("startup_fn", lambda: 1, ComputeScope.STARTUP)
        registry.register("request_fn", lambda: 2, ComputeScope.REQUEST)
        assert registry.get_scope("startup_fn") == ComputeScope.STARTUP
        assert registry.get_scope("request_fn") == ComputeScope.REQUEST

    def test_get_scope_returns_none_for_missing(self):
        """Test get_scope() returns None for missing function."""
        registry = ComputeRegistry()
        assert registry.get_scope("missing") is None

    def test_default_scope_is_startup(self):
        """Test default scope is STARTUP."""
        registry = ComputeRegistry()
        registry.register("fn", lambda: 1)
        assert registry.get_scope("fn") == ComputeScope.STARTUP

    def test_unregister_removes_function(self):
        """Test unregister() removes a function."""
        registry = ComputeRegistry()
        registry.register("fn", lambda: 1)
        assert registry.unregister("fn") is True
        assert registry.has("fn") is False

    def test_unregister_returns_false_for_missing(self):
        """Test unregister() returns False for missing function."""
        registry = ComputeRegistry()
        assert registry.unregister("missing") is False

    def test_clear_removes_all_functions(self):
        """Test clear() removes all functions."""
        registry = ComputeRegistry()
        registry.register("fn1", lambda: 1)
        registry.register("fn2", lambda: 2)
        registry.clear()
        assert registry.has("fn1") is False
        assert registry.has("fn2") is False
        assert registry.list() == []
