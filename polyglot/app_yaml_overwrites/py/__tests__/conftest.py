"""
Pytest configuration and shared fixtures for app_yaml_overwrites.
"""
import logging
import os
import sys
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, AsyncMock
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ==============================================================================
# Mock external dependencies before importing app_yaml_overwrites modules
# ==============================================================================

# Mock app_yaml_static_config module
mock_app_yaml_static_config = MagicMock()
mock_app_yaml_static_config.AppYamlConfig = MagicMock()
mock_app_yaml_static_config.AppYamlConfig.get_instance = MagicMock(return_value=MagicMock(
    get_all=MagicMock(return_value={})
))
sys.modules['app_yaml_static_config'] = mock_app_yaml_static_config

# Mock runtime_template_resolver module
mock_runtime_template_resolver = MagicMock()
mock_runtime_template_resolver.create_resolver = MagicMock(return_value=MagicMock(
    resolve_object=AsyncMock(return_value={})
))
mock_runtime_template_resolver.ComputeScope = MagicMock()
mock_runtime_template_resolver.ComputeScope.STARTUP = 'STARTUP'
mock_runtime_template_resolver.ComputeScope.REQUEST = 'REQUEST'
sys.modules['runtime_template_resolver'] = mock_runtime_template_resolver

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@pytest.fixture
def mock_logger():
    """Fixture providing a mock logger for injection."""
    mock = MagicMock()
    mock.debug = MagicMock()
    mock.info = MagicMock()
    mock.warn = MagicMock()
    mock.error = MagicMock()
    mock.trace = MagicMock()
    return mock


@pytest.fixture
def assert_log_contains(caplog):
    """Fixture to assert log messages are present."""
    def _assert(expected_text: str, level: Optional[str] = None):
        for record in caplog.records:
            if level and record.levelname != level.upper():
                continue
            if expected_text in record.message:
                return True

        all_messages = [f"[{r.levelname}] {r.message}" for r in caplog.records]
        raise AssertionError(
            f"Expected log containing '{expected_text}' not found.\n"
            f"Captured logs:\n" + "\n".join(all_messages)
        )
    return _assert


@pytest.fixture
def clean_env(monkeypatch):
    """Fixture to manage environment variables."""
    def set_env(**kwargs):
        for key, value in kwargs.items():
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, value)
    return set_env


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "app": {
            "name": "Test App",
            "version": "1.0.0"
        },
        "providers": {
            "test_provider": {
                "base_url": "https://api.test.com",
                "headers": {
                    "X-App-Name": None,
                    "X-Custom": "static-value"
                },
                "overwrite_from_context": {
                    "headers": {
                        "X-App-Name": "{{app.name}}",
                        "X-Token": "{{fn:compute_token}}"
                    }
                }
            }
        },
        "storage": {
            "redis": {
                "host": "localhost",
                "port": 6379
            }
        }
    }


@pytest.fixture
def mock_app_yaml_config(sample_config):
    """Mock AppYamlConfig for testing without real YAML files."""
    mock = MagicMock()
    mock.get_all.return_value = sample_config
    mock.get_instance = MagicMock(return_value=mock)
    return mock


@pytest.fixture
def mock_context_extender():
    """Mock context extender function."""
    async def extender(context: Dict[str, Any], request: Any) -> Dict[str, Any]:
        return {"custom_key": "custom_value"}
    return extender
