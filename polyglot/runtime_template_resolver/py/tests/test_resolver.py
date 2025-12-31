"""
Unit tests for TemplateResolver.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
- Log verification (hyper-observability)
"""
import pytest

from runtime_template_resolver import (
    TemplateResolver,
    MissingStrategy,
    ResolverOptions,
    SecurityError,
    ValidationError,
    MissingValueError,
)


class TestTemplateResolver:
    """Tests for TemplateResolver."""

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_resolve_simple_placeholder(self, sample_context):
            """Happy path: resolves simple placeholder."""
            resolver = TemplateResolver()
            result = resolver.resolve("Hello {{name}}!", sample_context)
            assert result == "Hello World!"

        def test_resolve_nested_path(self, sample_context):
            """Resolves nested object paths."""
            resolver = TemplateResolver()
            result = resolver.resolve("User: {{user.profile.name}}", sample_context)
            assert result == "User: Alice"

        def test_resolve_array_access(self, sample_context):
            """Resolves array element access."""
            resolver = TemplateResolver()
            result = resolver.resolve("First: {{items[0]}}", sample_context)
            assert result == "First: apple"

        def test_resolve_multiple_placeholders(self, sample_context):
            """Resolves multiple placeholders in one template."""
            resolver = TemplateResolver()
            result = resolver.resolve("{{name}} has {{count}} items", sample_context)
            assert result == "World has 42 items"

        def test_resolve_no_placeholders(self):
            """Returns template unchanged when no placeholders."""
            resolver = TemplateResolver()
            result = resolver.resolve("No placeholders here", {})
            assert result == "No placeholders here"

        def test_resolve_object_recursive(self, sample_context, complex_object):
            """Recursively resolves templates in objects."""
            resolver = TemplateResolver()
            result = resolver.resolve_object(complex_object, sample_context)
            assert result["message"] == "Hello World!"
            assert result["greeting"] == "Welcome Alice"
            assert result["items"][0] == "First: apple"
            assert result["nested"]["value"] == "Count is 42"

    class TestDecisionBranchCoverage:
        """Test all if/else/switch branches."""

        def test_default_value_with_quotes(self):
            """Tests default value with double quotes."""
            resolver = TemplateResolver()
            result = resolver.resolve('Value: {{missing | "Default"}}', {})
            assert result == "Value: Default"

        def test_default_value_with_single_quotes(self):
            """Tests default value with single quotes."""
            resolver = TemplateResolver()
            result = resolver.resolve("Value: {{missing | 'Fallback'}}", {})
            assert result == "Value: Fallback"

        def test_default_value_without_quotes(self):
            """Tests default value without quotes."""
            resolver = TemplateResolver()
            result = resolver.resolve("Value: {{missing | N/A}}", {})
            assert result == "Value: N/A"

        def test_missing_strategy_empty(self, sample_context):
            """Tests EMPTY missing strategy."""
            resolver = TemplateResolver()
            opts = ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
            result = resolver.resolve("Missing: {{missing}}", sample_context, options=opts)
            assert result == "Missing: "

        def test_missing_strategy_keep(self, sample_context):
            """Tests KEEP missing strategy."""
            resolver = TemplateResolver()
            opts = ResolverOptions(missing_strategy=MissingStrategy.KEEP)
            result = resolver.resolve("Missing: {{missing}}", sample_context, options=opts)
            assert result == "Missing: {{missing}}"

        def test_missing_strategy_error(self, sample_context):
            """Tests ERROR missing strategy."""
            resolver = TemplateResolver()
            opts = ResolverOptions(missing_strategy=MissingStrategy.ERROR, throw_on_error=True)
            with pytest.raises(MissingValueError):
                resolver.resolve("Missing: {{missing}}", sample_context, options=opts)

        def test_throw_on_error_true(self):
            """Tests throw_on_error=True."""
            resolver = TemplateResolver()
            opts = ResolverOptions(throw_on_error=True)
            with pytest.raises(SecurityError):
                resolver.resolve("Bad: {{_private}}", {}, options=opts)

        def test_throw_on_error_false(self):
            """Tests throw_on_error=False keeps original."""
            resolver = TemplateResolver()
            opts = ResolverOptions(throw_on_error=False)
            result = resolver.resolve("Bad: {{_private}}", {}, options=opts)
            assert result == "Bad: {{_private}}"

        def test_list_access_with_index(self, sample_context):
            """Tests list access with valid index."""
            resolver = TemplateResolver()
            result = resolver.resolve("Item: {{items[1]}}", sample_context)
            assert result == "Item: banana"

        def test_list_access_with_non_numeric_key(self, sample_context):
            """Tests list access with non-numeric key returns empty."""
            resolver = TemplateResolver()
            opts = ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
            result = resolver.resolve("Item: {{items.foo}}", sample_context, options=opts)
            assert result == "Item: "

        def test_dict_access(self, sample_context):
            """Tests dict access."""
            resolver = TemplateResolver()
            result = resolver.resolve("Email: {{user.profile.email}}", sample_context)
            assert result == "Email: alice@example.com"

        def test_null_context_value(self, sample_context):
            """Tests resolving null value in context."""
            resolver = TemplateResolver()
            opts = ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
            result = resolver.resolve("Null: {{nullable}}", sample_context, options=opts)
            assert result == "Null: "

    class TestBoundaryValueAnalysis:
        """Test edge cases: empty, min, max, boundary values."""

        def test_empty_template(self):
            """Boundary: empty template string."""
            resolver = TemplateResolver()
            result = resolver.resolve("", {})
            assert result == ""

        def test_template_with_only_placeholder(self):
            """Boundary: template is just a placeholder."""
            resolver = TemplateResolver()
            result = resolver.resolve("{{name}}", {"name": "Test"})
            assert result == "Test"

        def test_deeply_nested_path(self, sample_context):
            """Boundary: deeply nested path resolution."""
            resolver = TemplateResolver()
            result = resolver.resolve("Deep: {{nested.deep.value}}", sample_context)
            assert result == "Deep: found"

        def test_array_first_element(self, sample_context):
            """Boundary: first array element."""
            resolver = TemplateResolver()
            result = resolver.resolve("{{items[0]}}", sample_context)
            assert result == "apple"

        def test_array_last_element(self, sample_context):
            """Boundary: last array element."""
            resolver = TemplateResolver()
            result = resolver.resolve("{{items[2]}}", sample_context)
            assert result == "cherry"

        def test_array_out_of_bounds(self, sample_context):
            """Boundary: array index out of bounds."""
            resolver = TemplateResolver()
            opts = ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
            result = resolver.resolve("{{items[99]}}", sample_context, options=opts)
            assert result == ""

        def test_multiple_consecutive_placeholders(self):
            """Boundary: multiple consecutive placeholders."""
            resolver = TemplateResolver()
            result = resolver.resolve("{{a}}{{b}}{{c}}", {"a": "1", "b": "2", "c": "3"})
            assert result == "123"

        def test_placeholder_with_spaces(self):
            """Boundary: placeholder with extra spaces."""
            resolver = TemplateResolver()
            result = resolver.resolve("{{  name  }}", {"name": "Test"})
            assert result == "Test"

        def test_boolean_value_coercion(self, sample_context):
            """Boundary: boolean value coerced to string."""
            resolver = TemplateResolver()
            result = resolver.resolve("Active: {{active}}", sample_context)
            assert result == "Active: True"

        def test_numeric_value_coercion(self, sample_context):
            """Boundary: numeric value coerced to string."""
            resolver = TemplateResolver()
            result = resolver.resolve("Count: {{count}}", sample_context)
            assert result == "Count: 42"

        def test_object_value_coercion(self, sample_context):
            """Boundary: object value coerced to JSON string."""
            resolver = TemplateResolver()
            result = resolver.resolve("User: {{user.profile}}", sample_context)
            assert '"name": "Alice"' in result or "'name': 'Alice'" in result

        def test_list_value_coercion(self, sample_context):
            """Boundary: list value coerced to JSON string."""
            resolver = TemplateResolver()
            result = resolver.resolve("Roles: {{user.roles}}", sample_context)
            assert "admin" in result and "user" in result

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        def test_security_error_private_attribute(self):
            """Access to private attribute raises SecurityError."""
            resolver = TemplateResolver()
            opts = ResolverOptions(throw_on_error=True)
            with pytest.raises(SecurityError, match="private/unsafe"):
                resolver.resolve("{{_secret}}", {}, options=opts)

        def test_security_error_double_underscore(self):
            """Access to dunder attribute raises SecurityError."""
            resolver = TemplateResolver()
            opts = ResolverOptions(throw_on_error=True)
            with pytest.raises(SecurityError, match="private/unsafe"):
                resolver.resolve("{{__class__}}", {}, options=opts)

        def test_empty_placeholder_not_matched(self):
            """Empty placeholder {{}} is not matched by regex, returned as-is."""
            resolver = TemplateResolver()
            result = resolver.resolve("{{}}", {})
            assert result == "{{}}"

        def test_validation_error_invalid_characters(self):
            """Invalid characters raise ValidationError."""
            resolver = TemplateResolver()
            opts = ResolverOptions(throw_on_error=True)
            with pytest.raises(ValidationError, match="Invalid"):
                resolver.resolve("{{foo@bar}}", {}, options=opts)

        def test_validation_error_double_dots(self):
            """Double dots in path raise ValidationError."""
            resolver = TemplateResolver()
            opts = ResolverOptions(throw_on_error=True)
            with pytest.raises(ValidationError, match="empty segment"):
                resolver.resolve("{{foo..bar}}", {}, options=opts)

        def test_error_without_throw_keeps_original(self):
            """Error without throw_on_error keeps original placeholder."""
            resolver = TemplateResolver()
            result = resolver.resolve("Bad: {{_private}}", {})
            assert result == "Bad: {{_private}}"

    class TestLogVerification:
        """Verify defensive logging at control flow points."""

        def test_logs_resolve_called(self, capsys, sample_context):
            """Verify resolve logs entry."""
            resolver = TemplateResolver()
            resolver.resolve("Hello {{name}}", sample_context)
            captured = capsys.readouterr()
            assert "resolve() called" in captured.out

        def test_logs_security_warning(self, capsys):
            """Verify security violation is logged."""
            resolver = TemplateResolver()
            resolver.resolve("{{_private}}", {})
            captured = capsys.readouterr()
            assert "private/unsafe" in captured.out

        def test_logs_error_on_failure(self, capsys):
            """Verify errors are logged."""
            resolver = TemplateResolver()
            resolver.resolve("{{_bad}}", {})
            captured = capsys.readouterr()
            assert "_bad" in captured.out or "private" in captured.out

    class TestIntegration:
        """End-to-end scenarios with realistic data."""

        def test_real_world_email_template(self):
            """Integration: realistic email template."""
            resolver = TemplateResolver()
            template = """
            Dear {{customer.name}},

            Thank you for your order #{{order.id}}.
            Total: ${{order.total}}

            Best regards,
            {{company.name}}
            """
            context = {
                "customer": {"name": "John Doe"},
                "order": {"id": "12345", "total": "99.99"},
                "company": {"name": "ACME Corp"}
            }
            result = resolver.resolve(template, context)
            assert "Dear John Doe" in result
            assert "order #12345" in result
            assert "$99.99" in result
            assert "ACME Corp" in result

        def test_config_template_with_defaults(self):
            """Integration: configuration with defaults."""
            resolver = TemplateResolver()
            template = '{"host": "{{db.host | "localhost"}}", "port": "{{db.port | "5432"}}"}'
            result = resolver.resolve(template, {})
            assert '"host": "localhost"' in result
            assert '"port": "5432"' in result

        def test_resolve_object_with_nested_templates(self):
            """Integration: deeply nested object resolution."""
            resolver = TemplateResolver()
            obj = {
                "config": {
                    "database": {
                        "url": "postgres://{{db.host}}:{{db.port}}/{{db.name}}"
                    }
                },
                "templates": [
                    "Welcome {{user}}",
                    "Goodbye {{user}}"
                ]
            }
            context = {
                "db": {"host": "localhost", "port": "5432", "name": "mydb"},
                "user": "Alice"
            }
            result = resolver.resolve_object(obj, context)
            assert result["config"]["database"]["url"] == "postgres://localhost:5432/mydb"
            assert result["templates"][0] == "Welcome Alice"
            assert result["templates"][1] == "Goodbye Alice"
