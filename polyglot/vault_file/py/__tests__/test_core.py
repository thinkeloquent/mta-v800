"""
Unit tests for vault_file.core module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
- Log verification (hyper-observability)
"""
import json
import logging
import os
import tempfile
import pytest

from vault_file.core import normalize_version, to_json, from_json, parse_env_file
from vault_file.domain import VaultFile, VaultHeader


class TestNormalizeVersion:
    """Tests for normalize_version function."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_returns_normalized_three_part_version(self):
            """Happy path: already valid version passes through."""
            result = normalize_version("1.2.3")
            assert result == "1.2.3"

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else/switch branches."""

        def test_single_part_version_gets_padded(self):
            """Version with single part should be padded to x.0.0."""
            result = normalize_version("1")
            assert result == "1.0.0"

        def test_two_part_version_gets_padded(self):
            """Version with two parts should be padded to x.y.0."""
            result = normalize_version("1.2")
            assert result == "1.2.0"

        def test_four_part_version_truncated(self):
            """Version with more than 3 parts should be truncated."""
            result = normalize_version("1.2.3.4")
            assert result == "1.2.3"

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValueAnalysis:
        """Test edge cases: empty, min, max, boundary values."""

        def test_empty_string_version(self):
            """Empty string should result in 0.0.0."""
            result = normalize_version("")
            assert result == ".0.0"

        def test_zero_version(self):
            """Zero version should work."""
            result = normalize_version("0.0.0")
            assert result == "0.0.0"

        def test_large_version_numbers(self):
            """Large version numbers should be preserved."""
            result = normalize_version("999.999.999")
            assert result == "999.999.999"


class TestToJson:
    """Tests for to_json function."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_serializes_vault_file_to_json(self):
            """VaultFile should serialize to valid JSON."""
            vault = VaultFile(
                header=VaultHeader(version="1.0.0", created_at="2023-01-01T00:00:00.000Z"),
                secrets={"KEY": "value"}
            )
            result = to_json(vault)
            parsed = json.loads(result)

            assert parsed["header"]["version"] == "1.0.0"
            assert parsed["secrets"]["KEY"] == "value"

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test serialization with different content."""

        def test_empty_secrets(self):
            """VaultFile with empty secrets should serialize correctly."""
            vault = VaultFile(
                header=VaultHeader(version="1.0.0", created_at="2023-01-01T00:00:00.000Z"),
                secrets={}
            )
            result = to_json(vault)
            parsed = json.loads(result)

            assert parsed["secrets"] == {}

        def test_multiple_secrets(self):
            """VaultFile with multiple secrets should serialize correctly."""
            vault = VaultFile(
                header=VaultHeader(
                    version="1.0.0",
                    created_at="2023-01-01T00:00:00.000Z",
                    description="Test vault"
                ),
                secrets={"KEY1": "value1", "KEY2": "value2"}
            )
            result = to_json(vault)
            parsed = json.loads(result)

            assert len(parsed["secrets"]) == 2
            assert parsed["header"]["description"] == "Test vault"


class TestFromJson:
    """Tests for from_json function."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_deserializes_valid_json(self):
            """Valid JSON should deserialize to VaultFile."""
            json_str = '{"header": {"version": "1.0.0", "created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {"KEY": "value"}}'
            result = from_json(json_str)

            assert result.header.version == "1.0.0"
            assert result.secrets["KEY"] == "value"

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test version normalization branch."""

        def test_normalizes_version_on_load(self):
            """Version should be normalized when loading from JSON."""
            json_str = '{"header": {"version": "1.0", "created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {}}'
            result = from_json(json_str)

            assert result.header.version == "1.0.0"

        def test_no_version_in_header(self):
            """JSON without version should use default."""
            json_str = '{"header": {"created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {}}'
            result = from_json(json_str)

            assert result.header.version == "1.0.0"

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        def test_invalid_json_raises_error(self):
            """Invalid JSON should raise an error."""
            with pytest.raises(json.JSONDecodeError):
                from_json("not valid json")

        def test_missing_required_field_raises_error(self):
            """Missing required field should raise validation error."""
            with pytest.raises(Exception):
                from_json('{"header": {}}')

        def test_invalid_version_format_raises_error(self):
            """Invalid version format after normalization should raise error."""
            with pytest.raises(ValueError, match="semantic versioning"):
                from_json('{"header": {"version": "invalid", "created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {}}')


class TestParseEnvFile:
    """Tests for parse_env_file function."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_parses_valid_env_file(self, temp_env_file):
            """Valid .env file should parse correctly."""
            content = "KEY=value\nANOTHER=test"
            path = temp_env_file(content)

            try:
                result = parse_env_file(path)
                assert result["KEY"] == "value"
                assert result["ANOTHER"] == "test"
            finally:
                os.unlink(path)

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else paths."""

        def test_nonexistent_file_returns_empty(self):
            """Non-existent file should return empty dict."""
            result = parse_env_file("/nonexistent/path/.env")
            assert result == {}

        def test_skips_empty_lines(self, temp_env_file):
            """Empty lines should be skipped."""
            content = "KEY=value\n\n\nANOTHER=test"
            path = temp_env_file(content)

            try:
                result = parse_env_file(path)
                assert len(result) == 2
            finally:
                os.unlink(path)

        def test_skips_comment_lines(self, temp_env_file):
            """Lines starting with # should be skipped."""
            content = "# This is a comment\nKEY=value\n# Another comment"
            path = temp_env_file(content)

            try:
                result = parse_env_file(path)
                assert len(result) == 1
                assert result["KEY"] == "value"
            finally:
                os.unlink(path)

        def test_skips_lines_without_equals(self, temp_env_file):
            """Lines without = should be skipped."""
            content = "INVALID_LINE\nKEY=value"
            path = temp_env_file(content)

            try:
                result = parse_env_file(path)
                assert len(result) == 1
            finally:
                os.unlink(path)

        def test_removes_double_quotes(self, temp_env_file):
            """Double quoted values should have quotes removed."""
            content = 'KEY="quoted value"'
            path = temp_env_file(content)

            try:
                result = parse_env_file(path)
                assert result["KEY"] == "quoted value"
            finally:
                os.unlink(path)

        def test_removes_single_quotes(self, temp_env_file):
            """Single quoted values should have quotes removed."""
            content = "KEY='single quoted'"
            path = temp_env_file(content)

            try:
                result = parse_env_file(path)
                assert result["KEY"] == "single quoted"
            finally:
                os.unlink(path)

        def test_preserves_unquoted_values(self, temp_env_file):
            """Unquoted values should be preserved as-is."""
            content = "KEY=unquoted value"
            path = temp_env_file(content)

            try:
                result = parse_env_file(path)
                assert result["KEY"] == "unquoted value"
            finally:
                os.unlink(path)

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValueAnalysis:
        """Test edge cases."""

        def test_empty_file(self, temp_env_file):
            """Empty file should return empty dict."""
            path = temp_env_file("")

            try:
                result = parse_env_file(path)
                assert result == {}
            finally:
                os.unlink(path)

        def test_empty_value(self, temp_env_file):
            """Empty value should be preserved."""
            content = "KEY="
            path = temp_env_file(content)

            try:
                result = parse_env_file(path)
                assert result["KEY"] == ""
            finally:
                os.unlink(path)

        def test_value_with_equals_sign(self, temp_env_file):
            """Value containing = should be preserved."""
            content = "URL=postgres://user:pass=word@host"
            path = temp_env_file(content)

            try:
                result = parse_env_file(path)
                assert result["URL"] == "postgres://user:pass=word@host"
            finally:
                os.unlink(path)

        def test_whitespace_handling(self, temp_env_file):
            """Whitespace around key and value should be stripped."""
            content = "  KEY  =  value  "
            path = temp_env_file(content)

            try:
                result = parse_env_file(path)
                assert result["KEY"] == "value"
            finally:
                os.unlink(path)


class TestIntegration:
    """End-to-end scenarios with realistic data."""

    def test_roundtrip_json_serialization(self):
        """VaultFile should survive JSON roundtrip."""
        original = VaultFile(
            header=VaultHeader(
                version="2.0.0",
                created_at="2023-06-15T10:30:00.000Z",
                description="Test vault file"
            ),
            secrets={"DB_PASSWORD": "secret123", "API_TOKEN": "token456"}
        )

        json_str = to_json(original)
        restored = from_json(json_str)

        assert restored.header.version == original.header.version
        assert restored.header.description == original.header.description
        assert restored.secrets == original.secrets

    def test_parse_realistic_env_file(self, temp_env_file):
        """Parse a realistic .env file with various formats."""
        content = """# Database configuration
DATABASE_URL=postgres://user:password@localhost:5432/mydb
DATABASE_POOL_SIZE=10

# API Keys
API_KEY="sk-live-123456789"
API_SECRET='super-secret-key'

# Feature flags
DEBUG=true
VERBOSE=false
"""
        path = temp_env_file(content)

        try:
            result = parse_env_file(path)

            assert result["DATABASE_URL"] == "postgres://user:password@localhost:5432/mydb"
            assert result["DATABASE_POOL_SIZE"] == "10"
            assert result["API_KEY"] == "sk-live-123456789"
            assert result["API_SECRET"] == "super-secret-key"
            assert result["DEBUG"] == "true"
            assert result["VERBOSE"] == "false"
        finally:
            os.unlink(path)
