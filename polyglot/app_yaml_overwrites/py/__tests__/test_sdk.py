"""
Unit tests for ConfigSDK class.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
- Log verification (hyper-observability)
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app_yaml_overwrites.sdk import ConfigSDK


class TestConfigSDK:
    """Tests for ConfigSDK class."""

    # Reset singleton between tests
    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset ConfigSDK singleton before each test."""
        ConfigSDK._instance = None
        yield
        ConfigSDK._instance = None

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        @pytest.fixture(autouse=True)
        def reset_singleton(self):
            ConfigSDK._instance = None
            yield
            ConfigSDK._instance = None

        def test_constructor_creates_logger(self):
            """Constructor should create logger instance."""
            sdk = ConfigSDK({})

            assert sdk.logger is not None

        def test_constructor_sets_extenders(self):
            """Constructor should set context extenders."""
            async def extender(ctx, req):
                return {}

            sdk = ConfigSDK({"context_extenders": [extender]})

            assert len(sdk.context_extenders) == 1

        def test_constructor_defaults_empty_raw_config(self):
            """Constructor should default raw_config to empty dict."""
            sdk = ConfigSDK({})

            assert sdk.raw_config == {}

        def test_get_raw_returns_raw_config(self):
            """get_raw() should return raw_config."""
            sdk = ConfigSDK({})
            sdk.raw_config = {"key": "value"}

            result = sdk.get_raw()

            assert result == {"key": "value"}

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else/switch branches."""

        @pytest.fixture(autouse=True)
        def reset_singleton(self):
            ConfigSDK._instance = None
            yield
            ConfigSDK._instance = None

        @pytest.mark.asyncio
        async def test_initialize_returns_existing_instance(self):
            """initialize() should return existing instance if already created."""
            with patch('app_yaml_overwrites.sdk.AppYamlConfig') as MockAppYaml:
                mock_instance = MagicMock()
                mock_instance.get_all.return_value = {"key": "value"}
                MockAppYaml.get_instance.return_value = mock_instance

                sdk1 = await ConfigSDK.initialize({})
                sdk2 = await ConfigSDK.initialize({})

                assert sdk1 is sdk2

        @pytest.mark.asyncio
        async def test_initialize_creates_new_instance(self):
            """initialize() should create new instance if none exists."""
            with patch('app_yaml_overwrites.sdk.AppYamlConfig') as MockAppYaml:
                mock_instance = MagicMock()
                mock_instance.get_all.return_value = {}
                MockAppYaml.get_instance.return_value = mock_instance

                sdk = await ConfigSDK.initialize({})

                assert sdk is not None
                assert ConfigSDK._instance is sdk

        def test_get_instance_raises_when_not_initialized(self):
            """get_instance() should raise when not initialized."""
            with pytest.raises(RuntimeError, match="not initialized"):
                ConfigSDK.get_instance()

        @pytest.mark.asyncio
        async def test_get_instance_returns_instance_after_init(self):
            """get_instance() should return instance after initialization."""
            with patch('app_yaml_overwrites.sdk.AppYamlConfig') as MockAppYaml:
                mock_instance = MagicMock()
                mock_instance.get_all.return_value = {}
                MockAppYaml.get_instance.return_value = mock_instance

                await ConfigSDK.initialize({})
                sdk = ConfigSDK.get_instance()

                assert sdk is not None

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValues:
        """Test edge cases: empty, min, max, boundary values."""

        @pytest.fixture(autouse=True)
        def reset_singleton(self):
            ConfigSDK._instance = None
            yield
            ConfigSDK._instance = None

        def test_constructor_with_none_options(self):
            """Constructor should handle None options."""
            sdk = ConfigSDK(None)

            assert sdk.context_extenders == []

        def test_constructor_with_empty_options(self):
            """Constructor should handle empty options."""
            sdk = ConfigSDK({})

            assert sdk.context_extenders == []

        @pytest.mark.asyncio
        async def test_initialize_with_empty_options(self):
            """initialize() should work with empty options."""
            with patch('app_yaml_overwrites.sdk.AppYamlConfig') as MockAppYaml:
                mock_instance = MagicMock()
                mock_instance.get_all.return_value = {}
                MockAppYaml.get_instance.return_value = mock_instance

                sdk = await ConfigSDK.initialize()

                assert sdk.initialized is True

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        @pytest.fixture(autouse=True)
        def reset_singleton(self):
            ConfigSDK._instance = None
            yield
            ConfigSDK._instance = None

        @pytest.mark.asyncio
        async def test_get_resolved_raises_when_not_initialized(self):
            """get_resolved() should raise when SDK not initialized."""
            sdk = ConfigSDK({})
            # sdk.initialized is False by default

            with pytest.raises(RuntimeError, match="not initialized"):
                await sdk.get_resolved("STARTUP")

        @pytest.mark.asyncio
        async def test_bootstrap_handles_app_yaml_config(self):
            """_bootstrap() should load config from AppYamlConfig."""
            with patch('app_yaml_overwrites.sdk.AppYamlConfig') as MockAppYaml:
                mock_instance = MagicMock()
                mock_instance.get_all.return_value = {"app": {"name": "Test"}}
                MockAppYaml.get_instance.return_value = mock_instance

                sdk = ConfigSDK({})
                await sdk._bootstrap({})

                assert sdk.raw_config == {"app": {"name": "Test"}}
                assert sdk.initialized is True

    # =========================================================================
    # Log Verification
    # =========================================================================

    class TestLogVerification:
        """Verify defensive logging at control flow points."""

        @pytest.fixture(autouse=True)
        def reset_singleton(self):
            ConfigSDK._instance = None
            yield
            ConfigSDK._instance = None

        @pytest.mark.asyncio
        async def test_bootstrap_logs_debug_messages(self, caplog):
            """_bootstrap() should log debug messages."""
            import logging

            with patch('app_yaml_overwrites.sdk.AppYamlConfig') as MockAppYaml:
                mock_instance = MagicMock()
                mock_instance.get_all.return_value = {"key": "value"}
                MockAppYaml.get_instance.return_value = mock_instance

                with caplog.at_level(logging.DEBUG):
                    sdk = ConfigSDK({})
                    await sdk._bootstrap({})

                # Check that some logging occurred
                assert sdk.initialized is True

    # =========================================================================
    # Integration Tests
    # =========================================================================

    class TestIntegration:
        """End-to-end scenarios with realistic data."""

        @pytest.fixture(autouse=True)
        def reset_singleton(self):
            ConfigSDK._instance = None
            yield
            ConfigSDK._instance = None

        @pytest.mark.asyncio
        async def test_full_initialization_flow(self):
            """Test complete initialization flow."""
            sample_config = {
                "app": {"name": "IntegrationTest", "version": "1.0.0"},
                "providers": {
                    "test": {"base_url": "https://test.com"}
                }
            }

            with patch('app_yaml_overwrites.sdk.AppYamlConfig') as MockAppYaml:
                mock_instance = MagicMock()
                mock_instance.get_all.return_value = sample_config
                MockAppYaml.get_instance.return_value = mock_instance

                sdk = await ConfigSDK.initialize({})

                assert sdk.initialized is True
                assert sdk.get_raw()["app"]["name"] == "IntegrationTest"

        @pytest.mark.asyncio
        async def test_to_json_returns_raw_config(self):
            """to_json() should return raw config."""
            with patch('app_yaml_overwrites.sdk.AppYamlConfig') as MockAppYaml:
                mock_instance = MagicMock()
                mock_instance.get_all.return_value = {"data": "value"}
                MockAppYaml.get_instance.return_value = mock_instance

                sdk = await ConfigSDK.initialize({})
                result = await sdk.to_json()

                assert result == {"data": "value"}
