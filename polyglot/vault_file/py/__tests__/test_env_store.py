"""
Unit tests for vault_file.env_store module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
- Log verification (hyper-observability)
"""
import logging
import os
import tempfile
import pytest

from vault_file.env_store import EnvStore
from vault_file.validators import EnvKeyNotFoundError


class TestEnvStore:
    """Tests for EnvStore singleton class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_get_instance_returns_singleton(self, reset_env_store):
            """get_instance should return the same instance."""
            instance1 = EnvStore.get_instance()
            instance2 = EnvStore.get_instance()

            assert instance1 is instance2

        def test_on_startup_initializes_store(self, reset_env_store, temp_env_file):
            """on_startup should initialize the store."""
            content = "TEST_KEY=test_value"
            path = temp_env_file(content)

            try:
                result = EnvStore.on_startup(path)
                assert result.total_vars_loaded > 0
                assert EnvStore.is_initialized()
            finally:
                os.unlink(path)

        def test_get_returns_value_from_store(self, reset_env_store, temp_env_file):
            """get should return value from internal store."""
            content = "STORE_KEY=store_value"
            path = temp_env_file(content)

            try:
                EnvStore.on_startup(path)
                value = EnvStore.get("STORE_KEY")
                assert value == "store_value"
            finally:
                os.unlink(path)

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else paths."""

        def test_get_from_internal_store_priority(self, reset_env_store, temp_env_file, monkeypatch):
            """Internal store should take priority over os.environ."""
            monkeypatch.setenv("PRIORITY_KEY", "from_environ")
            content = "PRIORITY_KEY=from_store"
            path = temp_env_file(content)

            try:
                EnvStore.on_startup(path)
                value = EnvStore.get("PRIORITY_KEY")
                assert value == "from_store"
            finally:
                os.unlink(path)

        def test_get_from_os_environ_fallback(self, reset_env_store, monkeypatch):
            """Should fallback to os.environ if not in store."""
            monkeypatch.setenv("ENVIRON_KEY", "environ_value")
            EnvStore.on_startup("/nonexistent/.env")

            value = EnvStore.get("ENVIRON_KEY")
            assert value == "environ_value"

        def test_get_returns_default_when_not_found(self, reset_env_store):
            """Should return default when key not found."""
            EnvStore.on_startup("/nonexistent/.env")

            value = EnvStore.get("NONEXISTENT_KEY", "default_value")
            assert value == "default_value"

        def test_get_returns_none_when_no_default(self, reset_env_store):
            """Should return None when key not found and no default."""
            EnvStore.on_startup("/nonexistent/.env")

            value = EnvStore.get("NONEXISTENT_KEY")
            assert value is None

        def test_on_startup_with_nonexistent_file(self, reset_env_store, caplog):
            """on_startup should warn when file not found."""
            with caplog.at_level(logging.WARNING):
                EnvStore.on_startup("/nonexistent/.env")

            assert EnvStore.is_initialized()

        def test_on_startup_with_existing_file(self, reset_env_store, temp_env_file, caplog):
            """on_startup should load vars from existing file."""
            content = "FILE_KEY=file_value"
            path = temp_env_file(content)

            try:
                with caplog.at_level(logging.DEBUG):
                    result = EnvStore.on_startup(path)

                assert EnvStore.get("FILE_KEY") == "file_value"
            finally:
                os.unlink(path)

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValueAnalysis:
        """Test edge cases."""

        def test_empty_env_file(self, reset_env_store, temp_env_file):
            """Empty env file should result in empty store."""
            path = temp_env_file("")

            try:
                EnvStore.on_startup(path)
                assert EnvStore.is_initialized()
            finally:
                os.unlink(path)

        def test_key_with_empty_value(self, reset_env_store, temp_env_file):
            """Key with empty value should be stored."""
            content = "EMPTY_KEY="
            path = temp_env_file(content)

            try:
                EnvStore.on_startup(path)
                value = EnvStore.get("EMPTY_KEY")
                assert value == ""
            finally:
                os.unlink(path)

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        def test_get_or_throw_raises_on_missing_key(self, reset_env_store):
            """get_or_throw should raise EnvKeyNotFoundError for missing key."""
            EnvStore.on_startup("/nonexistent/.env")

            with pytest.raises(EnvKeyNotFoundError) as exc_info:
                EnvStore.get_or_throw("MISSING_KEY")

            assert exc_info.value.key == "MISSING_KEY"

        def test_get_or_throw_returns_value_when_found(self, reset_env_store, temp_env_file):
            """get_or_throw should return value when key exists."""
            content = "REQUIRED_KEY=required_value"
            path = temp_env_file(content)

            try:
                EnvStore.on_startup(path)
                value = EnvStore.get_or_throw("REQUIRED_KEY")
                assert value == "required_value"
            finally:
                os.unlink(path)

        def test_get_or_throw_returns_environ_value(self, reset_env_store, monkeypatch):
            """get_or_throw should return os.environ value."""
            monkeypatch.setenv("ENV_REQUIRED", "env_value")
            EnvStore.on_startup("/nonexistent/.env")

            value = EnvStore.get_or_throw("ENV_REQUIRED")
            assert value == "env_value"

    # =========================================================================
    # Log Verification
    # =========================================================================

    class TestLogVerification:
        """Verify defensive logging at control flow points."""

        def test_logs_initialization_start(self, reset_env_store, temp_env_file, caplog):
            """Should log when starting initialization."""
            path = temp_env_file("KEY=value")

            try:
                with caplog.at_level(logging.INFO):
                    EnvStore.on_startup(path)

                assert any("Starting EnvStore initialization" in r.message for r in caplog.records)
            finally:
                os.unlink(path)

        def test_logs_initialization_complete(self, reset_env_store, temp_env_file, caplog):
            """Should log when initialization completes."""
            path = temp_env_file("KEY=value")

            try:
                with caplog.at_level(logging.INFO):
                    EnvStore.on_startup(path)

                assert any("EnvStore initialized" in r.message for r in caplog.records)
            finally:
                os.unlink(path)

        def test_logs_file_not_found_warning(self, reset_env_store, caplog):
            """Should log warning when file not found."""
            with caplog.at_level(logging.WARNING):
                EnvStore.on_startup("/nonexistent/path/.env")

            assert any("not found" in r.message for r in caplog.records)

        def test_logs_missing_key_on_get_or_throw(self, reset_env_store, caplog):
            """Should log error when required key is missing."""
            EnvStore.on_startup("/nonexistent/.env")

            with caplog.at_level(logging.ERROR):
                with pytest.raises(EnvKeyNotFoundError):
                    EnvStore.get_or_throw("MISSING")

            assert any("missing" in r.message.lower() for r in caplog.records)

    # =========================================================================
    # Integration
    # =========================================================================

    class TestIntegration:
        """End-to-end scenarios with realistic data."""

        def test_full_workflow(self, reset_env_store, temp_env_file, monkeypatch):
            """Test complete workflow: startup, get, get_or_throw."""
            monkeypatch.setenv("SYSTEM_VAR", "system_value")

            content = """# Database config
DATABASE_URL=postgres://localhost/db
API_KEY="secret-api-key"
DEBUG=true
"""
            path = temp_env_file(content)

            try:
                result = EnvStore.on_startup(path)

                assert result.total_vars_loaded > 0
                assert EnvStore.is_initialized()

                assert EnvStore.get("DATABASE_URL") == "postgres://localhost/db"
                assert EnvStore.get("API_KEY") == "secret-api-key"
                assert EnvStore.get("DEBUG") == "true"
                assert EnvStore.get("SYSTEM_VAR") == "system_value"
                assert EnvStore.get("MISSING", "default") == "default"

                assert EnvStore.get_or_throw("DATABASE_URL") == "postgres://localhost/db"

            finally:
                os.unlink(path)
