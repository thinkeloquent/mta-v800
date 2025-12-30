"""
Unit tests for app_yaml_static_config.sdk module.

Tests cover:
- SDK initialization methods
- Read-only data access
- JSON serialization safety
- Provider/Service/Storage listing
"""
import pytest
from pathlib import Path

from app_yaml_static_config.sdk import AppYamlConfigSDK
from app_yaml_static_config.core import AppYamlConfig
from app_yaml_static_config.types import InitOptions


class TestAppYamlConfigSDK:
    """Tests for AppYamlConfigSDK class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_from_directory_initializes_sdk(self, fixtures_dir):
            """from_directory should initialize SDK from config directory."""
            sdk = AppYamlConfigSDK.from_directory(str(fixtures_dir))

            assert sdk is not None
            assert isinstance(sdk, AppYamlConfigSDK)

        def test_get_returns_json_safe_value(self, fixtures_dir):
            """get() should return JSON-serializable value."""
            sdk = AppYamlConfigSDK.from_directory(str(fixtures_dir))

            result = sdk.get("app")
            assert result is not None
            assert result["name"] == "test-app"

        def test_get_nested_returns_json_safe_value(self, fixtures_dir):
            """get_nested() should return JSON-serializable value."""
            sdk = AppYamlConfigSDK.from_directory(str(fixtures_dir))

            result = sdk.get_nested(["app", "name"])
            assert result == "test-app"

        def test_get_all_returns_json_safe_dict(self, fixtures_dir):
            """get_all() should return complete config as JSON-safe dict."""
            sdk = AppYamlConfigSDK.from_directory(str(fixtures_dir))

            result = sdk.get_all()
            assert isinstance(result, dict)
            assert "app" in result

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else branches."""

        def test_list_providers_returns_provider_names(self, fixtures_dir):
            """list_providers() should return list of provider names."""
            sdk = AppYamlConfigSDK.from_directory(str(fixtures_dir))

            providers = sdk.list_providers()
            assert isinstance(providers, list)
            assert "anthropic" in providers
            assert "openai" in providers

        def test_list_services_returns_service_names(self, fixtures_dir):
            """list_services() should return list of service names."""
            sdk = AppYamlConfigSDK.from_directory(str(fixtures_dir))

            services = sdk.list_services()
            assert isinstance(services, list)
            assert "database" in services
            assert "cache" in services

        def test_list_storages_returns_storage_names(self, fixtures_dir):
            """list_storages() should return list of storage names."""
            sdk = AppYamlConfigSDK.from_directory(str(fixtures_dir))

            storages = sdk.list_storages()
            assert isinstance(storages, list)
            assert "local" in storages
            assert "s3" in storages

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValues:
        """Test edge cases."""

        def test_get_missing_key_returns_none(self, fixtures_dir):
            """get() with missing key should return None."""
            sdk = AppYamlConfigSDK.from_directory(str(fixtures_dir))

            result = sdk.get("nonexistent_key")
            assert result is None

        def test_list_providers_empty_when_none_defined(self, empty_config_path, fixtures_dir):
            """list_providers() should return empty list when no providers."""
            # Reset singleton and initialize with empty config
            AppYamlConfig._instance = None
            AppYamlConfig._config = {}
            AppYamlConfig._original_configs = {}

            options = InitOptions(
                files=[empty_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            sdk = AppYamlConfigSDK(AppYamlConfig.get_instance())

            providers = sdk.list_providers()
            assert providers == []

    # =========================================================================
    # Integration
    # =========================================================================

    class TestIntegration:
        """End-to-end scenarios."""

        def test_sdk_reflects_merged_config(self, base_config_path, override_config_path, fixtures_dir):
            """SDK should reflect merged configuration from multiple files."""
            # Reset and initialize with multiple files
            AppYamlConfig._instance = None
            AppYamlConfig._config = {}
            AppYamlConfig._original_configs = {}

            options = InitOptions(
                files=[base_config_path, override_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            sdk = AppYamlConfigSDK(AppYamlConfig.get_instance())

            # Check merged values
            app_config = sdk.get("app")
            assert app_config["environment"] == "production"  # From override
            assert app_config["name"] == "test-app"  # From base

        def test_sdk_values_are_immutable(self, fixtures_dir):
            """Values returned by SDK should not affect internal state."""
            sdk = AppYamlConfigSDK.from_directory(str(fixtures_dir))

            # Get and modify
            config = sdk.get_all()
            config["app"]["name"] = "modified"

            # Get again - should be unchanged
            config2 = sdk.get_all()
            assert config2["app"]["name"] == "test-app"
