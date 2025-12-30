"""
Unit tests for vault_file.sdk module.

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
from unittest.mock import MagicMock, patch

from vault_file.sdk import VaultFileSDK, VaultFileSDKBuilder
from vault_file.env_store import EnvStore


# Note: EnvStore singleton is reset by autouse fixture in conftest.py


@pytest.fixture
def mock_logger():
    """Create a mock logger that doesn't cause logging errors."""
    mock = MagicMock()
    mock.debug = MagicMock()
    mock.info = MagicMock()
    mock.warn = MagicMock()
    mock.error = MagicMock()
    return mock


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file."""
    created_files = []

    def _create(content: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            created_files.append(f.name)
            return f.name

    yield _create

    # Cleanup all created files
    for f in created_files:
        try:
            os.unlink(f)
        except:
            pass


class TestVaultFileSDK:
    """Tests for VaultFileSDK class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_create_returns_builder(self):
            """create() should return a builder instance."""
            builder = VaultFileSDK.create()
            assert isinstance(builder, VaultFileSDKBuilder)

        def test_build_returns_sdk(self):
            """build() should return SDK instance."""
            sdk = VaultFileSDK.create().build()
            assert isinstance(sdk, VaultFileSDK)

        def test_load_config_returns_result(self, temp_env_file, mock_logger):
            """load_config should return SDKResult."""
            path = temp_env_file("KEY=value")
            sdk = VaultFileSDK.create().with_env_path(path).with_logger(mock_logger).build()

            result = sdk.load_config()
            assert result.success is True
            assert result.data is not None

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else paths."""

        def test_load_from_path_file_exists(self, temp_env_file, mock_logger):
            """load_from_path should succeed for existing file."""
            content = "KEY1=val1\nKEY2=val2"
            path = temp_env_file(content)
            sdk = VaultFileSDK.create().with_logger(mock_logger).build()

            result = sdk.load_from_path(path)
            assert result.success is True
            assert result.data.total_vars_loaded == 2

        def test_load_from_path_file_not_found(self, mock_logger):
            """load_from_path should fail for missing file."""
            sdk = VaultFileSDK.create().with_logger(mock_logger).build()

            result = sdk.load_from_path("/nonexistent/path/.env")

            assert result.success is False
            assert result.error.code == "FILE_NOT_FOUND"

        def test_validate_file_valid(self, temp_env_file, mock_logger):
            """validate_file should succeed for valid file."""
            path = temp_env_file("VALID_KEY=value")
            sdk = VaultFileSDK.create().with_logger(mock_logger).build()

            result = sdk.validate_file(path)
            assert result.success is True
            assert result.data.valid is True
            assert result.data.errors == []

        def test_validate_file_not_found(self, mock_logger):
            """validate_file should fail for missing file."""
            sdk = VaultFileSDK.create().with_logger(mock_logger).build()

            result = sdk.validate_file("/nonexistent/.env")

            assert result.success is False
            assert result.error.code == "FILE_NOT_FOUND"

        def test_export_to_format_not_implemented(self, mock_logger):
            """export_to_format should return not implemented."""
            sdk = VaultFileSDK.create().with_logger(mock_logger).build()

            result = sdk.export_to_format("json", "/some/path")

            assert result.success is False
            assert result.error.code == "NOT_IMPLEMENTED"

    # =========================================================================
    # Agent Operations
    # =========================================================================

    class TestAgentOperations:
        """Test agent-facing SDK operations."""

        def test_describe_config(self, temp_env_file, mock_logger):
            """describe_config should return config description."""
            path = temp_env_file("KEY=value")
            sdk = VaultFileSDK.create().with_env_path(path).with_logger(mock_logger).build()
            sdk.load_config()

            result = sdk.describe_config()
            assert result.success is True
            assert result.data.version == "1.0.0"
            assert path in result.data.sources

        def test_get_secret_safe_exists(self, temp_env_file, mock_logger):
            """get_secret_safe should return masked secret info when exists."""
            path = temp_env_file("SECRET_KEY=secret_value")
            sdk = VaultFileSDK.create().with_env_path(path).with_logger(mock_logger).build()
            sdk.load_config()

            result = sdk.get_secret_safe("SECRET_KEY")
            assert result.success is True
            assert result.data.key == "SECRET_KEY"
            assert result.data.exists is True
            assert result.data.masked == "***"

        def test_get_secret_safe_not_exists(self):
            """get_secret_safe should indicate when secret doesn't exist."""
            sdk = VaultFileSDK.create().build()
            EnvStore.on_startup("/nonexistent/.env")

            result = sdk.get_secret_safe("NONEXISTENT_KEY")

            assert result.success is True
            assert result.data.exists is False
            assert result.data.masked == ""

        def test_list_available_keys(self):
            """list_available_keys should return empty list (not implemented)."""
            sdk = VaultFileSDK.create().build()

            result = sdk.list_available_keys()

            assert result.success is True
            assert result.data == []

    # =========================================================================
    # DEV Tool Operations
    # =========================================================================

    class TestDevToolOperations:
        """Test developer tool operations."""

        def test_diagnose_env_store_initialized(self, temp_env_file, mock_logger):
            """diagnose_env_store should report initialized state."""
            path = temp_env_file("KEY=value")
            sdk = VaultFileSDK.create().with_env_path(path).with_logger(mock_logger).build()
            sdk.load_config()

            result = sdk.diagnose_env_store()
            assert result.success is True
            assert result.data.initialized is True

        def test_diagnose_env_store_not_initialized(self, mock_logger):
            """diagnose_env_store should report uninitialized state."""
            sdk = VaultFileSDK.create().with_logger(mock_logger).build()

            result = sdk.diagnose_env_store()

            assert result.success is True
            assert result.data.initialized is False

        def test_find_missing_required_all_present(self, temp_env_file, mock_logger):
            """find_missing_required should return empty when all present."""
            path = temp_env_file("KEY1=val1\nKEY2=val2")
            sdk = VaultFileSDK.create().with_env_path(path).with_logger(mock_logger).build()
            sdk.load_config()

            result = sdk.find_missing_required(["KEY1", "KEY2"])
            assert result.success is True
            assert result.data == []

        def test_find_missing_required_some_missing(self, temp_env_file, mock_logger):
            """find_missing_required should return missing keys."""
            path = temp_env_file("KEY1=val1")
            sdk = VaultFileSDK.create().with_env_path(path).with_logger(mock_logger).build()
            sdk.load_config()

            result = sdk.find_missing_required(["KEY1", "KEY2", "KEY3"])
            assert result.success is True
            assert "KEY2" in result.data
            assert "KEY3" in result.data
            assert "KEY1" not in result.data

        def test_suggest_missing_keys(self):
            """suggest_missing_keys should return empty list (not implemented)."""
            sdk = VaultFileSDK.create().build()

            result = sdk.suggest_missing_keys("DB_")

            assert result.success is True
            assert result.data == []

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        def test_load_config_handles_exception(self, mock_logger):
            """load_config should handle exceptions gracefully."""
            sdk = VaultFileSDK.create().with_env_path("/invalid/path/.env").with_logger(mock_logger).build()

            # Patch EnvStore.on_startup to raise an exception
            with patch.object(EnvStore, 'on_startup', side_effect=RuntimeError("Forced error")):
                result = sdk.load_config()

            assert result.success is False
            assert result.error.code == "LOAD_ERROR"


class TestVaultFileSDKBuilder:
    """Tests for VaultFileSDKBuilder class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_with_env_path(self):
            """with_env_path should set custom path."""
            sdk = VaultFileSDK.create().with_env_path("/custom/.env").build()
            assert sdk.env_path == "/custom/.env"

        def test_with_base64_parsers(self):
            """with_base64_parsers should set parsers."""
            parsers = {"json": lambda x: x}
            sdk = VaultFileSDK.create().with_base64_parsers(parsers).build()
            assert "json" in sdk.base64_parsers

        def test_with_logger(self):
            """with_logger should set custom logger."""
            mock_logger = MagicMock()
            sdk = VaultFileSDK.create().with_logger(mock_logger).build()
            assert sdk.logger == mock_logger

    # =========================================================================
    # Builder Chaining
    # =========================================================================

    class TestBuilderChaining:
        """Test builder method chaining."""

        def test_chain_all_methods(self):
            """All builder methods should be chainable."""
            mock_logger = MagicMock()
            sdk = (
                VaultFileSDK.create()
                .with_env_path("/custom/.env")
                .with_base64_parsers({"test": lambda x: x})
                .with_logger(mock_logger)
                .build()
            )

            assert sdk.env_path == "/custom/.env"
            assert "test" in sdk.base64_parsers
            assert sdk.logger == mock_logger
