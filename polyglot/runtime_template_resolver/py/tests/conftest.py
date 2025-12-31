"""
Pytest configuration and shared fixtures.
"""
import logging
from typing import Optional
from unittest.mock import MagicMock
import pytest

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
    mock.warning = MagicMock()
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
def sample_context():
    """Fixture providing sample context data."""
    return {
        "name": "World",
        "user": {
            "profile": {
                "name": "Alice",
                "age": 30,
                "email": "alice@example.com"
            },
            "roles": ["admin", "user"]
        },
        "items": ["apple", "banana", "cherry"],
        "count": 42,
        "active": True,
        "nullable": None,
        "nested": {
            "deep": {
                "value": "found"
            }
        }
    }


@pytest.fixture
def complex_object():
    """Fixture providing a complex object with templates."""
    return {
        "message": "Hello {{name}}!",
        "greeting": "Welcome {{user.profile.name}}",
        "items": [
            "First: {{items[0]}}",
            "Second: {{items[1]}}"
        ],
        "nested": {
            "value": "Count is {{count}}"
        }
    }
