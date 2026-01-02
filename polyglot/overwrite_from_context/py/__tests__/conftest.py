"""
Pytest configuration and shared fixtures.

Following FORMAT_TEST.yaml specification for:
- Log verification (hyper-observability)
- Mock logger injection
- Environment management
"""
import logging
import os
import sys
from typing import Any, Dict, Optional, List
from unittest.mock import MagicMock
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from runtime_template_resolver import create_registry, create_resolver, ComputeScope
from runtime_template_resolver.compute_registry import ComputeRegistry
from runtime_template_resolver.context_resolver import ContextResolver
from runtime_template_resolver.options import ResolverOptions

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class MockLogger:
    """Mock logger that captures log messages for verification."""

    def __init__(self):
        self.logs: Dict[str, List[Dict[str, Any]]] = {
            'debug': [],
            'info': [],
            'warn': [],
            'error': [],
            'trace': []
        }

    def debug(self, msg: str, *args, **kwargs) -> None:
        self.logs['debug'].append({'msg': msg, 'args': args, 'kwargs': kwargs})

    def info(self, msg: str, *args, **kwargs) -> None:
        self.logs['info'].append({'msg': msg, 'args': args, 'kwargs': kwargs})

    def warn(self, msg: str, *args, **kwargs) -> None:
        self.logs['warn'].append({'msg': msg, 'args': args, 'kwargs': kwargs})

    def error(self, msg: str, *args, **kwargs) -> None:
        self.logs['error'].append({'msg': msg, 'args': args, 'kwargs': kwargs})

    def trace(self, msg: str, *args, **kwargs) -> None:
        self.logs['trace'].append({'msg': msg, 'args': args, 'kwargs': kwargs})

    def contains(self, level: str, text: str) -> bool:
        """Check if log level contains message with text."""
        return any(text in entry['msg'] for entry in self.logs.get(level, []))

    def all_messages(self) -> List[str]:
        """Get all log messages as formatted strings."""
        messages = []
        for level, entries in self.logs.items():
            for entry in entries:
                messages.append(f"[{level.upper()}] {entry['msg']}")
        return messages


@pytest.fixture
def mock_logger():
    """Fixture providing a mock logger for injection."""
    return MockLogger()


@pytest.fixture
def registry(mock_logger):
    """Fixture providing a fresh ComputeRegistry instance."""
    return ComputeRegistry(logger=mock_logger)


@pytest.fixture
def resolver(registry, mock_logger):
    """Fixture providing a ContextResolver with mock logger."""
    options = ResolverOptions(logger=mock_logger)
    return ContextResolver(registry=registry, options=options)


@pytest.fixture
def assert_log_contains():
    """Fixture to assert log messages are present in MockLogger."""
    def _assert(logger: MockLogger, level: str, expected_text: str):
        if not logger.contains(level, expected_text):
            all_msgs = logger.all_messages()
            raise AssertionError(
                f"Expected log containing '{expected_text}' at level '{level}' not found.\n"
                f"Captured logs:\n" + "\n".join(all_msgs)
            )
        return True
    return _assert


@pytest.fixture
def clean_env(monkeypatch):
    """Fixture to manage environment variables."""
    original_env = dict(os.environ)

    def set_env(**kwargs):
        for key, value in kwargs.items():
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, str(value))

    yield set_env

    # Restore original environment
    for key in list(os.environ.keys()):
        if key not in original_env:
            del os.environ[key]


@pytest.fixture
def sample_config():
    """Fixture providing sample configuration for testing."""
    return {
        "app": {
            "name": "Test App",
            "version": "{{env.APP_VERSION | '1.0.0'}}",
            "debug": "{{env.DEBUG | 'false'}}"
        },
        "database": {
            "host": "{{env.DB_HOST | 'localhost'}}",
            "port": "{{env.DB_PORT | '5432'}}",
            "name": "{{env.DB_NAME | 'testdb'}}"
        },
        "computed": {
            "timestamp": "{{fn:get_timestamp}}",
            "request_id": "{{fn:get_request_id}}"
        }
    }
