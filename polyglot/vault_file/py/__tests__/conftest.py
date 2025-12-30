"""
Pytest configuration and shared fixtures for vault_file tests.
"""
import logging
import os
import tempfile
from typing import Any, Dict, Optional
from unittest.mock import MagicMock
import pytest


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
def temp_env_file():
    """Fixture to create a temporary .env file."""
    def _create(content: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            return f.name
    return _create


@pytest.fixture
def sample_env_content():
    """Sample .env file content for testing."""
    return """# Sample environment file
DATABASE_URL=postgres://localhost:5432/db
API_KEY="secret-key-123"
DEBUG=true
EMPTY_VALUE=
QUOTED_VALUE='single quoted'
"""


@pytest.fixture(autouse=True)
def reset_env_store():
    """Reset EnvStore singleton between tests (autouse=True applies to all tests)."""
    from vault_file.env_store import EnvStore
    # Reset singleton before test
    EnvStore._instance = None
    yield
    # Cleanup after test
    EnvStore._instance = None


@pytest.fixture
def sample_vault_file_json():
    """Sample VaultFile JSON for testing."""
    return '{"header": {"version": "1.0.0", "created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {"MY_SECRET": "value"}}'
