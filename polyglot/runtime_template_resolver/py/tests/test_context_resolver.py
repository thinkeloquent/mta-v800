"""Tests for ContextResolver module."""

import pytest
from runtime_template_resolver import (
    ComputeRegistry,
    ContextResolver,
    ComputeFunctionError,
)


class TestContextResolverTemplates:
    """Template resolution tests."""

    def test_resolve_simple_template(self):
        """Test resolving a simple template."""
        resolver = ContextResolver()
        result = resolver.resolve("Hello {{name}}!", {"name": "World"})
        assert result == "Hello World!"

    def test_resolve_nested_template(self):
        """Test resolving a nested template."""
        resolver = ContextResolver()
        result = resolver.resolve(
            "Welcome {{user.name}}!",
            {"user": {"name": "Alice"}}
        )
        assert result == "Welcome Alice!"

    def test_resolve_template_with_default(self):
        """Test resolving a template with default value."""
        resolver = ContextResolver()
        result = resolver.resolve(
            "Host: {{host | 'localhost'}}",
            {}
        )
        assert result == "Host: localhost"

    def test_resolve_multiple_placeholders(self):
        """Test resolving multiple placeholders."""
        resolver = ContextResolver()
        result = resolver.resolve(
            "{{greeting}}, {{name}}!",
            {"greeting": "Hello", "name": "World"}
        )
        assert result == "Hello, World!"


class TestContextResolverCompute:
    """Compute function resolution tests."""

    def test_resolve_compute_function(self):
        """Test resolving a compute function."""
        registry = ComputeRegistry()
        registry.register("get_port", lambda: 5432)
        resolver = ContextResolver(registry)
        result = resolver.resolve("{{fn:get_port}}", {})
        assert result == 5432

    def test_resolve_compute_function_with_context(self):
        """Test resolving a compute function that uses context."""
        registry = ComputeRegistry()
        registry.register("get_env_port", lambda ctx: ctx.get("PORT", 3000))
        resolver = ContextResolver(registry)
        result = resolver.resolve("{{fn:get_env_port}}", {"PORT": 8080})
        assert result == 8080

    def test_resolve_compute_function_with_whitespace(self):
        """Test resolving compute function with whitespace."""
        registry = ComputeRegistry()
        registry.register("get_value", lambda: 42)
        resolver = ContextResolver(registry)
        result = resolver.resolve("  {{fn:get_value}}  ", {})
        assert result == 42

    def test_resolve_unknown_compute_function(self):
        """Test that unknown compute function raises error."""
        resolver = ContextResolver()
        with pytest.raises(ComputeFunctionError, match="Unknown compute function"):
            resolver.resolve("{{fn:unknown}}", {})


class TestContextResolverPatternDetection:
    """Pattern detection tests."""

    def test_is_compute_pattern_true(self):
        """Test is_compute_pattern returns True for compute patterns."""
        resolver = ContextResolver()
        assert resolver.is_compute_pattern("{{fn:test}}") is True
        assert resolver.is_compute_pattern("  {{fn:test}}  ") is True
        assert resolver.is_compute_pattern("{{fn:get_value}}") is True

    def test_is_compute_pattern_false(self):
        """Test is_compute_pattern returns False for non-compute patterns."""
        resolver = ContextResolver()
        assert resolver.is_compute_pattern("{{name}}") is False
        assert resolver.is_compute_pattern("{{fn:test}} extra") is False
        assert resolver.is_compute_pattern("prefix {{fn:test}}") is False
        assert resolver.is_compute_pattern("{{user.name}}") is False
        assert resolver.is_compute_pattern("no placeholders") is False


class TestContextResolverObject:
    """Object resolution tests."""

    def test_resolve_object_with_templates(self):
        """Test resolving an object with templates."""
        resolver = ContextResolver()
        obj = {
            "host": "{{env.HOST}}",
            "name": "{{app.name}}"
        }
        context = {
            "env": {"HOST": "localhost"},
            "app": {"name": "myapp"}
        }
        result = resolver.resolve_object(obj, context)
        assert result == {"host": "localhost", "name": "myapp"}

    def test_resolve_object_with_compute(self):
        """Test resolving an object with compute functions."""
        registry = ComputeRegistry()
        registry.register("get_port", lambda: 5432)
        resolver = ContextResolver(registry)
        obj = {"port": "{{fn:get_port}}"}
        result = resolver.resolve_object(obj, {})
        assert result == {"port": 5432}

    def test_resolve_object_mixed(self):
        """Test resolving an object with both templates and compute."""
        registry = ComputeRegistry()
        registry.register("get_port", lambda: 5432)
        resolver = ContextResolver(registry)

        obj = {
            "host": "{{env.HOST}}",
            "port": "{{fn:get_port}}",
            "name": "static"
        }
        context = {"env": {"HOST": "localhost"}}

        result = resolver.resolve_object(obj, context)
        assert result == {
            "host": "localhost",
            "port": 5432,
            "name": "static"
        }

    def test_resolve_object_nested(self):
        """Test resolving a nested object."""
        registry = ComputeRegistry()
        registry.register("get_port", lambda: 5432)
        resolver = ContextResolver(registry)

        obj = {
            "database": {
                "host": "{{db.host}}",
                "port": "{{fn:get_port}}"
            },
            "api": {
                "url": "{{api.url}}"
            }
        }
        context = {
            "db": {"host": "db.example.com"},
            "api": {"url": "https://api.example.com"}
        }

        result = resolver.resolve_object(obj, context)
        assert result == {
            "database": {
                "host": "db.example.com",
                "port": 5432
            },
            "api": {
                "url": "https://api.example.com"
            }
        }

    def test_resolve_object_with_list(self):
        """Test resolving an object containing lists."""
        resolver = ContextResolver()
        obj = {
            "items": ["{{items[0]}}", "{{items[1]}}"]
        }
        context = {"items": ["first", "second"]}
        result = resolver.resolve_object(obj, context)
        assert result == {"items": ["first", "second"]}

    def test_resolve_object_preserves_non_strings(self):
        """Test that non-string values are preserved."""
        resolver = ContextResolver()
        obj = {
            "name": "{{name}}",
            "count": 42,
            "enabled": True,
            "data": None
        }
        result = resolver.resolve_object(obj, {"name": "test"})
        assert result == {
            "name": "test",
            "count": 42,
            "enabled": True,
            "data": None
        }


class TestContextResolverMany:
    """Resolve many tests."""

    def test_resolve_many_templates(self):
        """Test resolving multiple templates."""
        resolver = ContextResolver()
        expressions = ["{{name}}", "{{greeting}}"]
        results = resolver.resolve_many(expressions, {"name": "World", "greeting": "Hello"})
        assert results == ["World", "Hello"]

    def test_resolve_many_mixed(self):
        """Test resolving multiple mixed expressions."""
        registry = ComputeRegistry()
        registry.register("get_port", lambda: 5432)
        resolver = ContextResolver(registry)

        expressions = ["{{name}}", "{{fn:get_port}}"]
        results = resolver.resolve_many(expressions, {"name": "test"})
        assert results == ["test", 5432]

    def test_resolve_many_empty_list(self):
        """Test resolving empty list."""
        resolver = ContextResolver()
        results = resolver.resolve_many([], {})
        assert results == []


class TestContextResolverWithOptions:
    """Tests with resolver options."""

    def test_resolver_uses_default_options(self):
        """Test that resolver uses default options."""
        from runtime_template_resolver import ResolverOptions, MissingStrategy

        options = ResolverOptions(missing_strategy=MissingStrategy.KEEP)
        resolver = ContextResolver(options=options)

        result = resolver.resolve("{{missing}}", {})
        assert result == "{{missing}}"

    def test_resolver_overrides_options(self):
        """Test that options can be overridden per call."""
        from runtime_template_resolver import ResolverOptions, MissingStrategy

        default_options = ResolverOptions(missing_strategy=MissingStrategy.KEEP)
        resolver = ContextResolver(options=default_options)

        override_options = ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
        result = resolver.resolve("{{missing}}", {}, options=override_options)
        assert result == ""
