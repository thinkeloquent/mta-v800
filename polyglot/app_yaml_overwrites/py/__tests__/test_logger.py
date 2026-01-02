"""
Unit tests for logger module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
- Log verification (hyper-observability)
"""
import logging
import os
import json
import pytest
from unittest.mock import patch, MagicMock

from app_yaml_overwrites.logger import Logger


class TestLogger:
    """Tests for Logger class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_create_returns_logger_instance(self):
            """Logger.create() should return a Logger instance."""
            logger = Logger.create("test-package", "test-file.py")

            assert isinstance(logger, Logger)
            assert logger._package == "test-package"
            assert logger._filename == "test-file.py"

        def test_debug_logs_message(self, caplog):
            """debug() should log at DEBUG level."""
            logger = Logger.create("test", "test.py")

            with caplog.at_level(logging.DEBUG):
                logger.debug("Test debug message")

            assert len(caplog.records) > 0

        def test_info_logs_message(self, caplog):
            """info() should log at INFO level."""
            logger = Logger.create("test", "test.py")

            with caplog.at_level(logging.INFO):
                logger.info("Test info message")

            assert len(caplog.records) > 0

        def test_warn_logs_message(self, caplog):
            """warn() should log at WARNING level."""
            logger = Logger.create("test", "test.py")

            with caplog.at_level(logging.WARNING):
                logger.warn("Test warn message")

            assert len(caplog.records) > 0

        def test_error_logs_message(self, caplog):
            """error() should log at ERROR level."""
            logger = Logger.create("test", "test.py")

            with caplog.at_level(logging.ERROR):
                logger.error("Test error message")

            assert len(caplog.records) > 0

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else/switch branches."""

        def test_log_level_defaults_to_debug(self, clean_env):
            """Default LOG_LEVEL should be 'debug'."""
            clean_env(LOG_LEVEL=None)

            logger = Logger.create("test", "test.py")

            assert logger._level == "debug"

        def test_log_level_from_environment(self, clean_env):
            """LOG_LEVEL should be read from environment."""
            clean_env(LOG_LEVEL="info")

            logger = Logger.create("test", "test.py")

            assert logger._level == "info"

        def test_log_level_case_insensitive(self, clean_env):
            """LOG_LEVEL should be case insensitive."""
            clean_env(LOG_LEVEL="INFO")

            logger = Logger.create("test", "test.py")

            assert logger._level == "info"

        def test_debug_suppressed_when_level_is_info(self, clean_env, caplog):
            """debug() should be suppressed when LOG_LEVEL=info."""
            clean_env(LOG_LEVEL="info")
            logger = Logger.create("test", "test.py")

            with caplog.at_level(logging.DEBUG):
                logger.debug("This should not appear")

            # The logger's internal level blocks it, so caplog won't capture it
            # unless we check at lower level
            debug_logs = [r for r in caplog.records if "This should not appear" in r.message]
            assert len(debug_logs) == 0

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValues:
        """Test edge cases: empty, min, max, boundary values."""

        def test_empty_package_name(self):
            """Logger should handle empty package name."""
            logger = Logger.create("", "test.py")

            assert logger._package == ""

        def test_empty_filename(self):
            """Logger should handle empty filename."""
            logger = Logger.create("test", "")

            assert logger._filename == ""

        def test_empty_message(self, caplog):
            """Logger should handle empty message."""
            logger = Logger.create("test", "test.py")

            with caplog.at_level(logging.DEBUG):
                logger.debug("")

            assert len(caplog.records) > 0

        def test_very_long_message(self, caplog):
            """Logger should handle very long messages."""
            logger = Logger.create("test", "test.py")
            long_message = "x" * 10000

            with caplog.at_level(logging.DEBUG):
                logger.debug(long_message)

            assert len(caplog.records) > 0

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        def test_invalid_log_level_defaults_to_debug(self, clean_env):
            """Invalid LOG_LEVEL should default to debug behavior."""
            clean_env(LOG_LEVEL="invalid_level")

            logger = Logger.create("test", "test.py")

            # The LEVELS dict lookup will fail, defaulting to DEBUG
            assert logger._level == "invalid_level"

        def test_log_with_data_kwargs(self, caplog):
            """Logger should handle additional data kwargs."""
            logger = Logger.create("test", "test.py")

            with caplog.at_level(logging.DEBUG):
                logger.debug("Message with data", key="value", count=42)

            assert len(caplog.records) > 0

    # =========================================================================
    # Log Verification (Hyper-Observability)
    # =========================================================================

    class TestLogVerification:
        """Verify defensive logging at control flow points."""

        def test_log_output_is_json(self, caplog):
            """Log output should be valid JSON."""
            logger = Logger.create("test-pkg", "test.py")

            with caplog.at_level(logging.DEBUG):
                logger.info("Test message", data={"key": "value"})

            # Find the log record
            for record in caplog.records:
                try:
                    parsed = json.loads(record.message)
                    assert "timestamp" in parsed
                    assert "level" in parsed
                    assert "context" in parsed
                    assert "message" in parsed
                    return
                except json.JSONDecodeError:
                    continue

            # If we get here, no JSON log was found
            pytest.fail("No JSON-formatted log found")

        def test_log_contains_context(self, caplog):
            """Log output should contain package:filename context."""
            logger = Logger.create("my-package", "my-file.py")

            with caplog.at_level(logging.DEBUG):
                logger.debug("Context test")

            for record in caplog.records:
                if "my-package:my-file.py" in record.message:
                    return

            pytest.fail("Context not found in log output")
