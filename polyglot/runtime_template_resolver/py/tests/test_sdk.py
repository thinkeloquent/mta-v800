"""
Unit tests for SDK functions.

Tests cover:
- Statement coverage for all SDK functions
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
"""
import pytest

from runtime_template_resolver import (
    resolve,
    resolve_many,
    resolve_object,
    validate,
    extract,
    compile,
    validate_placeholder,
    extract_placeholders,
    ValidationError,
)


class TestSDK:
    """Tests for SDK functions."""

    class TestResolveFunction:
        """Tests for resolve() function."""

        def test_resolve_simple(self, sample_context):
            """Resolves simple template."""
            result = resolve("Hello {{name}}!", sample_context)
            assert result == "Hello World!"

        def test_resolve_nested(self, sample_context):
            """Resolves nested path."""
            result = resolve("User: {{user.profile.name}}", sample_context)
            assert result == "User: Alice"

        def test_resolve_with_default(self):
            """Resolves with default value."""
            result = resolve('Value: {{missing | "default"}}', {})
            assert result == "Value: default"

    class TestResolveManyFunction:
        """Tests for resolve_many() function."""

        def test_resolve_many_basic(self, sample_context):
            """Resolves multiple templates."""
            templates = [
                "Hello {{name}}!",
                "User: {{user.profile.name}}",
                "Count: {{count}}"
            ]
            results = resolve_many(templates, sample_context)
            assert results == [
                "Hello World!",
                "User: Alice",
                "Count: 42"
            ]

        def test_resolve_many_empty_list(self, sample_context):
            """Resolves empty list."""
            results = resolve_many([], sample_context)
            assert results == []

        def test_resolve_many_single_item(self, sample_context):
            """Resolves single item list."""
            results = resolve_many(["Hello {{name}}"], sample_context)
            assert results == ["Hello World"]

    class TestResolveObjectFunction:
        """Tests for resolve_object() function."""

        def test_resolve_object_dict(self, sample_context):
            """Resolves templates in dict."""
            obj = {"greeting": "Hello {{name}}!"}
            result = resolve_object(obj, sample_context)
            assert result["greeting"] == "Hello World!"

        def test_resolve_object_list(self, sample_context):
            """Resolves templates in list."""
            obj = ["Hello {{name}}", "Count: {{count}}"]
            result = resolve_object(obj, sample_context)
            assert result == ["Hello World", "Count: 42"]

        def test_resolve_object_nested(self, sample_context):
            """Resolves templates in nested structure."""
            obj = {
                "level1": {
                    "level2": {
                        "value": "{{name}}"
                    }
                }
            }
            result = resolve_object(obj, sample_context)
            assert result["level1"]["level2"]["value"] == "World"

        def test_resolve_object_non_string(self, sample_context):
            """Non-string values pass through unchanged."""
            obj = {"number": 42, "boolean": True}
            result = resolve_object(obj, sample_context)
            assert result["number"] == 42
            assert result["boolean"] is True

    class TestValidateFunction:
        """Tests for validate() function."""

        def test_validate_valid_template(self):
            """Valid template passes validation."""
            validate("Hello {{name}}!")

        def test_validate_nested_path(self):
            """Nested path passes validation."""
            validate("{{user.profile.name}}")

        def test_validate_with_default(self):
            """Template with default passes validation."""
            validate('{{missing | "default"}}')

        def test_validate_array_access(self):
            """Array access passes validation."""
            validate("{{items[0]}}")

        def test_validate_empty_placeholder_no_match(self):
            """Empty placeholder {{}} is not matched by regex, so no validation error."""
            # {{}} does not match the regex, so validate() finds no placeholders
            validate("{{}}")  # No error raised

        def test_validate_invalid_characters_raises(self):
            """Invalid characters raise ValidationError."""
            with pytest.raises(ValidationError, match="Invalid"):
                validate("{{foo@bar}}")

        def test_validate_double_dots_raises(self):
            """Double dots raise ValidationError."""
            with pytest.raises(ValidationError, match="empty segment"):
                validate("{{foo..bar}}")

    class TestExtractFunction:
        """Tests for extract() function."""

        def test_extract_single_placeholder(self):
            """Extracts single placeholder."""
            result = extract("Hello {{name}}!")
            assert result == ["name"]

        def test_extract_multiple_placeholders(self):
            """Extracts multiple placeholders."""
            result = extract("{{a}} and {{b}} and {{c}}")
            assert result == ["a", "b", "c"]

        def test_extract_no_placeholders(self):
            """Returns empty list when no placeholders."""
            result = extract("No placeholders here")
            assert result == []

        def test_extract_nested_path(self):
            """Extracts nested path."""
            result = extract("{{user.profile.name}}")
            assert result == ["user.profile.name"]

        def test_extract_with_default(self):
            """Extracts placeholder with default value."""
            result = extract('{{missing | "default"}}')
            assert result == ['missing | "default"']

    class TestCompileFunction:
        """Tests for compile() function."""

        def test_compile_returns_callable(self):
            """Compile returns callable function."""
            compiled = compile("Hello {{name}}!")
            assert callable(compiled)

        def test_compiled_function_resolves(self):
            """Compiled function resolves template."""
            compiled = compile("Hello {{name}}!")
            result = compiled({"name": "World"})
            assert result == "Hello World!"

        def test_compiled_function_reusable(self):
            """Compiled function is reusable."""
            compiled = compile("Count: {{count}}")
            assert compiled({"count": 1}) == "Count: 1"
            assert compiled({"count": 2}) == "Count: 2"
            assert compiled({"count": 3}) == "Count: 3"

    class TestValidatePlaceholderFunction:
        """Tests for validate_placeholder() function."""

        def test_valid_simple_key(self):
            """Valid simple key passes."""
            validate_placeholder("name")

        def test_valid_nested_key(self):
            """Valid nested key passes."""
            validate_placeholder("user.profile.name")

        def test_valid_array_index(self):
            """Valid array index passes."""
            validate_placeholder("items[0]")

        def test_empty_raises(self):
            """Empty placeholder raises."""
            with pytest.raises(ValidationError, match="empty"):
                validate_placeholder("")

        def test_whitespace_only_raises(self):
            """Whitespace-only raises."""
            with pytest.raises(ValidationError, match="empty"):
                validate_placeholder("   ")

        def test_invalid_chars_raises(self):
            """Invalid characters raise."""
            with pytest.raises(ValidationError, match="Invalid"):
                validate_placeholder("foo@bar")

    class TestExtractPlaceholdersFunction:
        """Tests for extract_placeholders() function."""

        def test_extract_basic(self):
            """Extracts basic placeholder."""
            result = extract_placeholders("{{name}}")
            assert result == ["name"]

        def test_extract_with_spaces(self):
            """Extracts placeholder and strips spaces."""
            result = extract_placeholders("{{  name  }}")
            assert result == ["name"]

        def test_extract_empty_template(self):
            """Returns empty for template without placeholders."""
            result = extract_placeholders("no placeholders")
            assert result == []
