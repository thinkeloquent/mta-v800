"""
Unit tests for vault_file.validators module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
"""
import pytest

from vault_file.validators import EnvKeyNotFoundError


class TestEnvKeyNotFoundError:
    """Tests for EnvKeyNotFoundError exception."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_creates_error_with_key(self):
            """Error should be created with key name."""
            error = EnvKeyNotFoundError("MY_KEY")

            assert error.key == "MY_KEY"
            assert "MY_KEY" in str(error)

        def test_error_message_format(self):
            """Error message should follow expected format."""
            error = EnvKeyNotFoundError("DATABASE_URL")

            assert str(error) == "Environment variable 'DATABASE_URL' not found"

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test different key formats."""

        def test_simple_key_name(self):
            """Simple key name should work."""
            error = EnvKeyNotFoundError("KEY")
            assert error.key == "KEY"

        def test_key_with_underscores(self):
            """Key with underscores should work."""
            error = EnvKeyNotFoundError("MY_LONG_KEY_NAME")
            assert error.key == "MY_LONG_KEY_NAME"

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValueAnalysis:
        """Test edge cases."""

        def test_empty_key(self):
            """Empty key should still create valid error."""
            error = EnvKeyNotFoundError("")
            assert error.key == ""
            assert "not found" in str(error)

        def test_key_with_special_characters(self):
            """Key with special characters should work."""
            error = EnvKeyNotFoundError("KEY-WITH-DASHES")
            assert error.key == "KEY-WITH-DASHES"

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test exception behavior."""

        def test_is_exception_subclass(self):
            """EnvKeyNotFoundError should be an Exception."""
            error = EnvKeyNotFoundError("KEY")
            assert isinstance(error, Exception)

        def test_can_be_raised_and_caught(self):
            """Error should be raiseable and catchable."""
            with pytest.raises(EnvKeyNotFoundError) as exc_info:
                raise EnvKeyNotFoundError("TEST_KEY")

            assert exc_info.value.key == "TEST_KEY"

        def test_can_be_caught_as_base_exception(self):
            """Error should be catchable as base Exception."""
            try:
                raise EnvKeyNotFoundError("MY_KEY")
            except Exception as e:
                assert "MY_KEY" in str(e)
