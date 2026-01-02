"""
Unit tests for Security module.

Tests cover:
- Path validation
- Blocked pattern detection
- Underscore prefix blocking
- Path traversal blocking

Following FORMAT_TEST.yaml specification.
"""
import pytest

from runtime_template_resolver.security import Security
from runtime_template_resolver.errors import SecurityError, ErrorCode


class TestSecurity:
    """Tests for Security class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_valid_path_passes(self):
            """Valid paths pass validation without raising."""
            Security.validate_path("database.host")
            Security.validate_path("app")
            Security.validate_path("config.server.port")
            Security.validate_path("a1.b2.c3")

        def test_simple_valid_path(self):
            """Single segment path validates."""
            Security.validate_path("hostname")

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else/switch branches."""

        def test_empty_path_raises(self):
            """Empty path raises SecurityError."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("")

            assert excinfo.value.code == ErrorCode.SECURITY_BLOCKED_PATH
            assert "empty" in str(excinfo.value).lower()

        def test_path_starting_with_number_raises(self):
            """Path starting with number raises SecurityError."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("123invalid")

            assert excinfo.value.code == ErrorCode.SECURITY_BLOCKED_PATH

        def test_path_starting_with_underscore_raises(self):
            """Path starting with underscore raises SecurityError."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("_private")

            assert excinfo.value.code == ErrorCode.SECURITY_BLOCKED_PATH

        def test_path_with_underscore_segment_raises(self):
            """Path with underscore prefix in segment raises."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("valid._internal")

            assert excinfo.value.code == ErrorCode.SECURITY_BLOCKED_PATH
            assert "_internal" in str(excinfo.value)

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValueAnalysis:
        """Test edge cases: blocked patterns, special characters."""

        def test_proto_blocked(self):
            """__proto__ is blocked."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("obj.__proto__")

            assert "__proto__" in str(excinfo.value)

        def test_class_blocked(self):
            """__class__ is blocked."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("obj.__class__")

            assert "__class__" in str(excinfo.value)

        def test_dict_blocked(self):
            """__dict__ is blocked."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("obj.__dict__")

            assert "__dict__" in str(excinfo.value)

        def test_constructor_blocked(self):
            """constructor is blocked."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("obj.constructor")

            assert "constructor" in str(excinfo.value)

        def test_prototype_blocked(self):
            """prototype is blocked."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("obj.prototype")

            assert "prototype" in str(excinfo.value)

        def test_path_traversal_blocked(self):
            """Path traversal (..) is blocked."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("a..b")

            assert excinfo.value.code == ErrorCode.SECURITY_BLOCKED_PATH
            assert ".." in str(excinfo.value)

        def test_special_characters_blocked(self):
            """Special characters are blocked."""
            invalid_paths = [
                "path-with-dash",
                "path with space",
                "path/with/slash",
                "path\\with\\backslash",
                "path@symbol",
                "path$dollar",
            ]

            for path in invalid_paths:
                with pytest.raises(SecurityError):
                    Security.validate_path(path)

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        def test_security_error_includes_path(self):
            """SecurityError includes the offending path."""
            with pytest.raises(SecurityError) as excinfo:
                Security.validate_path("bad.constructor.access")

            error = excinfo.value
            assert error.code == ErrorCode.SECURITY_BLOCKED_PATH
            assert error.context is not None

        def test_nested_blocked_pattern_detected(self):
            """Blocked pattern in nested path is detected."""
            with pytest.raises(SecurityError):
                Security.validate_path("deeply.nested.__proto__.path")

    # =========================================================================
    # Integration Tests
    # =========================================================================

    class TestIntegration:
        """Realistic security validation scenarios."""

        def test_realistic_config_paths(self):
            """Realistic configuration paths pass validation."""
            valid_paths = [
                "database.host",
                "database.port",
                "server.http.port",
                "app.name",
                "providers.aws.region",
                "services.api.timeout",
                "env.NODE_ENV",
                "secrets.apiKey",
            ]

            for path in valid_paths:
                Security.validate_path(path)  # Should not raise

        def test_attack_vectors_blocked(self):
            """Common attack vectors are blocked."""
            attack_paths = [
                "__proto__",
                "constructor.prototype",
                "a.__proto__.polluted",
                "_private_data",
                "user._password",
                "../../../etc/passwd",
                "..%2F..%2Fetc",
            ]

            for path in attack_paths:
                with pytest.raises(SecurityError):
                    Security.validate_path(path)
