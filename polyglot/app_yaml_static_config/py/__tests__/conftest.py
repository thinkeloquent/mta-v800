"""
Pytest configuration and shared fixtures for app_yaml_static_config.
"""
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock
import pytest

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Get fixtures directory (shared across polyglot implementations)
FIXTURES_DIR = Path(__file__).parent.parent.parent / "__fixtures__"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the shared fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def base_config_path(fixtures_dir: Path) -> str:
    """Return path to base.yaml fixture."""
    return str(fixtures_dir / "base.yaml")


@pytest.fixture
def override_config_path(fixtures_dir: Path) -> str:
    """Return path to override.yaml fixture."""
    return str(fixtures_dir / "override.yaml")


@pytest.fixture
def nested_config_path(fixtures_dir: Path) -> str:
    """Return path to nested.yaml fixture."""
    return str(fixtures_dir / "nested.yaml")


@pytest.fixture
def empty_config_path(fixtures_dir: Path) -> str:
    """Return path to empty.yaml fixture."""
    return str(fixtures_dir / "empty.yaml")


@pytest.fixture
def mock_logger() -> MagicMock:
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


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset AppYamlConfig singleton before each test."""
    from app_yaml_static_config.core import AppYamlConfig
    AppYamlConfig._instance = None
    AppYamlConfig._config = {}
    AppYamlConfig._original_configs = {}
    AppYamlConfig._initial_merged_config = None
    yield
    # Cleanup after test
    AppYamlConfig._instance = None
    AppYamlConfig._config = {}
    AppYamlConfig._original_configs = {}
    AppYamlConfig._initial_merged_config = None
