"""
Unit tests for app_yaml_static_config.core module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
- Log verification (hyper-observability)
"""
import pytest
from pathlib import Path

from app_yaml_static_config.core import AppYamlConfig
from app_yaml_static_config.types import InitOptions
from app_yaml_static_config.validators import ImmutabilityError


class TestAppYamlConfig:
    """Tests for AppYamlConfig singleton class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_initialize_creates_singleton(self, base_config_path, fixtures_dir):
            """Initialize should create and return singleton instance."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            instance = AppYamlConfig.initialize(options)

            assert instance is not None
            assert isinstance(instance, AppYamlConfig)

        def test_get_instance_returns_same_instance(self, base_config_path, fixtures_dir):
            """getInstance should return the same singleton."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            instance1 = AppYamlConfig.initialize(options)
            instance2 = AppYamlConfig.get_instance()

            assert instance1 is instance2

        def test_get_returns_top_level_value(self, base_config_path, fixtures_dir):
            """get() should return top-level configuration value."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            app_config = instance.get("app")
            assert app_config is not None
            assert app_config["name"] == "test-app"

        def test_get_nested_returns_deep_value(self, base_config_path, fixtures_dir):
            """get_nested() should traverse nested keys."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            value = instance.get_nested("app", "name")
            assert value == "test-app"

        def test_get_all_returns_deep_copy(self, base_config_path, fixtures_dir):
            """get_all() should return a deep copy of configuration."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            config1 = instance.get_all()
            config2 = instance.get_all()

            # Should be equal but not the same object
            assert config1 == config2
            assert config1 is not config2

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestDecisionBranchCoverage:
        """Test all if/else/switch branches."""

        def test_initialize_when_already_initialized(self, base_config_path, fixtures_dir):
            """Initialize when already initialized should return existing instance."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            instance1 = AppYamlConfig.initialize(options)
            instance2 = AppYamlConfig.initialize(options)

            assert instance1 is instance2

        def test_get_with_default_when_key_missing(self, base_config_path, fixtures_dir):
            """get() with missing key should return default."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            result = instance.get("nonexistent", "default_value")
            assert result == "default_value"

        def test_get_with_default_when_key_exists(self, base_config_path, fixtures_dir):
            """get() with existing key should return value, not default."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            result = instance.get("app", "default_value")
            assert result != "default_value"
            assert result["name"] == "test-app"

        def test_get_nested_returns_default_when_path_missing(self, base_config_path, fixtures_dir):
            """get_nested() should return default when path doesn't exist."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            result = instance.get_nested("app", "nonexistent", "path", default="fallback")
            assert result == "fallback"

        def test_get_original_with_file_returns_original(self, base_config_path, fixtures_dir):
            """get_original() with file should return that file's original config."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            original = instance.get_original(base_config_path)
            assert original is not None
            assert "app" in original

        def test_get_original_without_file_returns_empty(self, base_config_path, fixtures_dir):
            """get_original() without file should return empty dict."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            original = instance.get_original()
            assert original == {}

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValueAnalysis:
        """Test edge cases: empty, min, max, boundary values."""

        def test_empty_config_file(self, empty_config_path, fixtures_dir):
            """Loading empty config file should work."""
            options = InitOptions(
                files=[empty_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            config = instance.get_all()
            assert config == {}

        def test_get_nested_with_empty_keys(self, base_config_path, fixtures_dir):
            """get_nested() with empty path returns root config."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            # With no keys, returns the root config (not default)
            result = instance.get_nested(default="empty_default")
            assert result == instance.get_all()

        def test_deeply_nested_config(self, nested_config_path, fixtures_dir):
            """Should handle deeply nested configuration."""
            options = InitOptions(
                files=[nested_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            value = instance.get_nested("deeply", "nested", "config", "value")
            assert value == "found"

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        def test_get_instance_before_init_raises_error(self):
            """get_instance() before initialize should raise error."""
            with pytest.raises(Exception, match="not initialized"):
                AppYamlConfig.get_instance()

        def test_load_nonexistent_file_raises_error(self, fixtures_dir):
            """Loading nonexistent file should raise error."""
            options = InitOptions(
                files=["/nonexistent/path/config.yaml"],
                config_dir=str(fixtures_dir)
            )
            with pytest.raises(Exception):
                AppYamlConfig.initialize(options)

        def test_set_raises_immutability_error(self, base_config_path, fixtures_dir):
            """set() should raise ImmutabilityError."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            with pytest.raises(ImmutabilityError, match="immutable"):
                instance.set("key", "value")

        def test_update_raises_immutability_error(self, base_config_path, fixtures_dir):
            """update() should raise ImmutabilityError."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            with pytest.raises(ImmutabilityError, match="immutable"):
                instance.update({"key": "value"})

        def test_reset_raises_immutability_error(self, base_config_path, fixtures_dir):
            """reset() should raise ImmutabilityError."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            with pytest.raises(ImmutabilityError, match="immutable"):
                instance.reset()

        def test_clear_raises_immutability_error(self, base_config_path, fixtures_dir):
            """clear() should raise ImmutabilityError."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            with pytest.raises(ImmutabilityError, match="immutable"):
                instance.clear()

    # =========================================================================
    # Log Verification
    # =========================================================================

    class TestLogVerification:
        """Verify defensive logging at control flow points."""

        def test_initialize_logs_info(self, base_config_path, fixtures_dir, mock_logger):
            """Initialize should log info message."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir),
                logger=mock_logger
            )
            AppYamlConfig.initialize(options)

            mock_logger.info.assert_called()
            # Check that initialization was logged
            call_args = [str(call) for call in mock_logger.info.call_args_list]
            assert any("Initializing configuration" in arg for arg in call_args)

        def test_load_file_logs_debug(self, base_config_path, fixtures_dir, mock_logger):
            """Loading file should log debug message."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir),
                logger=mock_logger
            )
            AppYamlConfig.initialize(options)

            mock_logger.debug.assert_called()

    # =========================================================================
    # Integration
    # =========================================================================

    class TestIntegration:
        """End-to-end scenarios with realistic data."""

        def test_merge_multiple_config_files(self, base_config_path, override_config_path, fixtures_dir):
            """Multiple config files should merge correctly."""
            options = InitOptions(
                files=[base_config_path, override_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            # Override should take precedence
            app_env = instance.get_nested("app", "environment")
            assert app_env == "production"

            # Base values should be preserved
            app_name = instance.get_nested("app", "name")
            assert app_name == "test-app"

            # Override should add new keys
            app_debug = instance.get_nested("app", "debug")
            assert app_debug is False

            # Nested override should work
            db_port = instance.get_nested("services", "database", "port")
            assert db_port == 5433

        def test_restore_resets_to_initial_state(self, base_config_path, fixtures_dir):
            """restore() should reset config to initial merged state."""
            options = InitOptions(
                files=[base_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            # Get initial config
            initial_config = instance.get_all()

            # Restore should work (even though config is "immutable" to external callers)
            instance.restore()

            restored_config = instance.get_all()
            assert restored_config == initial_config

        def test_get_original_all_returns_all_files(self, base_config_path, override_config_path, fixtures_dir):
            """get_original_all() should return originals for all files."""
            options = InitOptions(
                files=[base_config_path, override_config_path],
                config_dir=str(fixtures_dir)
            )
            AppYamlConfig.initialize(options)
            instance = AppYamlConfig.get_instance()

            originals = instance.get_original_all()
            assert len(originals) == 2
            assert base_config_path in originals
            assert override_config_path in originals
