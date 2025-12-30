"""
Unit tests for app_yaml_static_config.validators module.

Tests cover:
- Error class instantiation
- Error message formatting
- Validation function behavior
"""
import pytest

from app_yaml_static_config.validators import (
    ConfigurationError,
    ImmutabilityError,
    validate_config_key,
)


class TestConfigurationError:
    """Tests for ConfigurationError class."""

    class TestStatementCoverage:
        """Ensure every statement executes."""

        def test_error_with_message_only(self):
            """Error should accept message only."""
            error = ConfigurationError("Test error")

            assert "Test error" in str(error)

        def test_error_with_message_and_context(self):
            """Error should include context in message."""
            error = ConfigurationError("Test error", context={"key": "value"})

            assert "Test error" in str(error)
            assert "context" in str(error)
            assert "key" in str(error)

    class TestBranchCoverage:
        """Test all branches."""

        def test_error_context_is_accessible(self):
            """Error context should be accessible."""
            context = {"file": "test.yaml", "line": 42}
            error = ConfigurationError("Parse error", context=context)

            assert error.context == context

        def test_error_context_none_by_default(self):
            """Error context should be None by default."""
            error = ConfigurationError("Test error")

            assert error.context is None


class TestImmutabilityError:
    """Tests for ImmutabilityError class."""

    class TestStatementCoverage:
        """Ensure every statement executes."""

        def test_immutability_error_is_configuration_error(self):
            """ImmutabilityError should be subclass of ConfigurationError."""
            error = ImmutabilityError("Cannot modify")

            assert isinstance(error, ConfigurationError)
            assert isinstance(error, Exception)

        def test_immutability_error_message(self):
            """ImmutabilityError should format message correctly."""
            error = ImmutabilityError("Configuration is immutable")

            assert "Configuration is immutable" in str(error)


class TestValidateConfigKey:
    """Tests for validate_config_key function."""

    class TestStatementCoverage:
        """Ensure every statement executes."""

        def test_valid_key_passes(self):
            """Valid key should not raise."""
            # Should not raise
            validate_config_key("valid_key")

    class TestBranchCoverage:
        """Test all branches."""

        def test_empty_string_raises_error(self):
            """Empty string should raise ConfigurationError."""
            with pytest.raises(ConfigurationError, match="empty"):
                validate_config_key("")

        def test_none_raises_error(self):
            """None should raise ConfigurationError."""
            with pytest.raises(ConfigurationError, match="empty"):
                validate_config_key(None)

    class TestBoundaryValues:
        """Test edge cases."""

        def test_whitespace_only_passes(self):
            """Whitespace-only string is technically not empty."""
            # Current implementation treats whitespace as valid
            # This documents the behavior
            validate_config_key("   ")

        def test_single_character_key_passes(self):
            """Single character key should be valid."""
            validate_config_key("a")
