"""
Unit tests for logger module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
- Log verification (hyper-observability)
"""
import json
import os
import pytest
from unittest.mock import MagicMock, patch

from logger import (
    logger,
    Logger,
    LoggerConfig,
    LoggerFactory,
    ContextLogger,
    LOG_LEVELS,
    extract_filename,
    format_human,
    format_json,
)


class TestLoggerConfig:
    """Tests for LoggerConfig class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_creates_config_with_defaults(self):
            """LoggerConfig should use defaults from environment."""
            config = LoggerConfig()
            assert config.level is not None
            assert config.colorize is not None
            assert config.timestamp is True
            assert config.json_format is not None

        def test_creates_config_with_custom_values(self):
            """LoggerConfig should accept custom values."""
            config = LoggerConfig(
                level="debug",
                colorize=False,
                timestamp=False,
                json_format=True,
            )
            assert config.level == "debug"
            assert config.colorize is False
            assert config.timestamp is False
            assert config.json_format is True

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else paths."""

        def test_level_from_env(self, clean_env):
            """Level should be read from LOG_LEVEL env var."""
            clean_env(LOG_LEVEL="debug")
            config = LoggerConfig()
            assert config.level == "debug"

        def test_level_default_when_no_env(self, clean_env):
            """Level should default to 'info' when no env var."""
            clean_env(LOG_LEVEL=None)
            config = LoggerConfig()
            assert config.level == "info"

        def test_colorize_disabled_by_no_color(self, clean_env):
            """Colorize should be disabled when NO_COLOR=1."""
            clean_env(NO_COLOR="1")
            config = LoggerConfig()
            assert config.colorize is False

        def test_colorize_enabled_by_default(self, clean_env):
            """Colorize should be enabled by default."""
            clean_env(NO_COLOR=None)
            config = LoggerConfig()
            assert config.colorize is True

        def test_json_format_from_env(self, clean_env):
            """JSON format should be read from LOG_FORMAT env var."""
            clean_env(LOG_FORMAT="json")
            config = LoggerConfig()
            assert config.json_format is True


class TestExtractFilename:
    """Tests for extract_filename function."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_extracts_filename_from_path(self):
            """extract_filename should return just the filename."""
            result = extract_filename("/path/to/file.py")
            assert result == "file.py"

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else paths."""

        def test_returns_unknown_for_empty(self):
            """extract_filename should return 'unknown' for empty string."""
            assert extract_filename("") == "unknown"

        def test_returns_unknown_for_none(self):
            """extract_filename should return 'unknown' for None."""
            assert extract_filename(None) == "unknown"

        def test_handles_simple_filename(self):
            """extract_filename should handle filename without path."""
            assert extract_filename("file.py") == "file.py"


class TestLogger:
    """Tests for Logger class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_creates_logger_instance(self, capture_output):
            """Logger should be created with package name and filename."""
            captured, output_fn = capture_output
            config = LoggerConfig(output=output_fn)
            log = Logger("test-package", __file__, config)

            assert log.package_name == "test-package"
            assert log.filename is not None

        def test_info_logs_message(self, capture_output):
            """info() should log at INFO level."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="info", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.info("Test message")
            assert len(captured) == 1
            assert "Test message" in captured[0]

        def test_debug_logs_message(self, capture_output):
            """debug() should log at DEBUG level."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="debug", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.debug("Debug message")
            assert len(captured) == 1
            assert "Debug message" in captured[0]

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else paths."""

        def test_skips_log_below_level(self, capture_output):
            """Logger should skip messages below current level."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="info", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.debug("Should not appear")
            assert len(captured) == 0

        def test_logs_at_or_above_level(self, capture_output):
            """Logger should log messages at or above current level."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="info", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.info("Should appear")
            log.warn("Should also appear")
            assert len(captured) == 2

        def test_logs_with_data(self, capture_output):
            """Logger should include data in output."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="info", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.info("With data", {"key": "value"})
            assert "key" in captured[0]

        def test_logs_with_error(self, capture_output):
            """Logger should include error in output."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="error", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.error("With error", error=ValueError("test error"))
            assert "test error" in captured[0]

        def test_json_format_output(self, capture_output):
            """Logger should output JSON when json_format is True."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="info", json_format=True, output=output_fn)
            log = Logger("test-package", __file__, config)

            log.info("JSON test")
            parsed = json.loads(captured[0])
            assert parsed["message"] == "JSON test"

    # =========================================================================
    # All Log Levels
    # =========================================================================

    class TestAllLogLevels:
        """Test all log level methods."""

        def test_log_method(self, capture_output):
            """log() should work as alias for info()."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="info", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.log("Log test")
            assert len(captured) == 1

        def test_warn_method(self, capture_output):
            """warn() should log at WARN level."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="warn", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.warn("Warning test")
            assert "Warning test" in captured[0]

        def test_warning_method(self, capture_output):
            """warning() should be alias for warn()."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="warn", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.warning("Warning alias test")
            assert "Warning alias test" in captured[0]

        def test_error_method(self, capture_output):
            """error() should log at ERROR level."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="error", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.error("Error test")
            assert "Error test" in captured[0]

        def test_trace_method(self, capture_output):
            """trace() should log at TRACE level."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="trace", output=output_fn)
            log = Logger("test-package", __file__, config)

            log.trace("Trace test")
            assert "Trace test" in captured[0]

    # =========================================================================
    # Child Logger
    # =========================================================================

    class TestChildLogger:
        """Test child logger creation."""

        def test_child_inherits_package(self, capture_output):
            """child() should inherit package name."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="info", output=output_fn)
            parent = Logger("parent-package", "parent.py", config)

            child = parent.child("child.py")
            assert child.package_name == "parent-package"
            assert child.filename == "child.py"

        def test_child_can_override_config(self, capture_output):
            """child() should allow config overrides."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="info", output=output_fn)
            parent = Logger("parent-package", "parent.py", config)

            child = parent.child("child.py", level="debug")
            assert child.config.level == "debug"


class TestContextLogger:
    """Tests for ContextLogger class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_creates_context_logger(self, capture_output):
            """with_context() should create ContextLogger."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="info", output=output_fn)
            parent = Logger("test-package", __file__, config)

            ctx_logger = parent.with_context({"request_id": "123"})
            assert isinstance(ctx_logger, ContextLogger)

        def test_context_merged_into_logs(self, capture_output):
            """ContextLogger should merge context into all logs."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="info", output=output_fn)
            parent = Logger("test-package", __file__, config)

            ctx_logger = parent.with_context({"request_id": "123"})
            ctx_logger.info("Test message")

            assert "request_id" in captured[0]
            assert "123" in captured[0]

    # =========================================================================
    # All Methods
    # =========================================================================

    class TestAllMethods:
        """Test all ContextLogger methods."""

        def test_all_log_methods(self, capture_output):
            """ContextLogger should have all log methods."""
            captured, output_fn = capture_output
            config = LoggerConfig(level="trace", output=output_fn)
            parent = Logger("test-package", __file__, config)
            ctx = parent.with_context({"ctx": "value"})

            ctx.log("log")
            ctx.info("info")
            ctx.warn("warn")
            ctx.warning("warning")
            ctx.error("error")
            ctx.debug("debug")
            ctx.trace("trace")

            assert len(captured) == 7


class TestLoggerFactory:
    """Tests for LoggerFactory class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_create_returns_logger(self):
            """LoggerFactory.create() should return Logger instance."""
            log = LoggerFactory.create("test-package", __file__)
            assert isinstance(log, Logger)

        def test_factory_has_log_levels(self):
            """LoggerFactory should expose LOG_LEVELS."""
            assert LoggerFactory.LOG_LEVELS == LOG_LEVELS

        def test_factory_has_default_config(self):
            """LoggerFactory should expose DEFAULT_CONFIG."""
            assert LoggerFactory.DEFAULT_CONFIG is not None

    # =========================================================================
    # Config Options
    # =========================================================================

    class TestConfigOptions:
        """Test factory configuration options."""

        def test_custom_level(self, capture_output):
            """Factory should accept custom level."""
            captured, output_fn = capture_output
            log = LoggerFactory.create("test", __file__, level="debug", output=output_fn)

            log.debug("Debug test")
            assert len(captured) == 1

        def test_custom_output(self, capture_output):
            """Factory should accept custom output function."""
            captured, output_fn = capture_output
            log = LoggerFactory.create("test", __file__, output=output_fn)

            log.info("Test")
            assert len(captured) == 1


class TestFormatFunctions:
    """Tests for format_human and format_json functions."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_format_human_basic(self):
            """format_human should format basic entry."""
            entry = {
                "timestamp": "2023-01-01T00:00:00Z",
                "level": "info",
                "package": "test",
                "filename": "test.py",
                "message": "Test message",
            }
            config = LoggerConfig(colorize=False)
            result = format_human(entry, config)
            assert "Test message" in result
            assert "INFO" in result

        def test_format_json_basic(self):
            """format_json should format basic entry."""
            entry = {
                "timestamp": "2023-01-01T00:00:00Z",
                "level": "info",
                "package": "test",
                "filename": "test.py",
                "message": "Test message",
            }
            result = format_json(entry)
            parsed = json.loads(result)
            assert parsed["message"] == "Test message"

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else paths."""

        def test_format_human_with_data(self):
            """format_human should include data."""
            entry = {
                "timestamp": "2023-01-01T00:00:00Z",
                "level": "info",
                "package": "test",
                "filename": "test.py",
                "message": "Test",
                "data": {"key": "value"},
            }
            config = LoggerConfig(colorize=False)
            result = format_human(entry, config)
            assert "key" in result

        def test_format_human_with_error(self):
            """format_human should include error traceback."""
            entry = {
                "timestamp": "2023-01-01T00:00:00Z",
                "level": "error",
                "package": "test",
                "filename": "test.py",
                "message": "Error",
                "error": ValueError("test error"),
            }
            config = LoggerConfig(colorize=False)
            result = format_human(entry, config)
            assert "ValueError" in result

        def test_format_json_with_error(self):
            """format_json should serialize error."""
            error = ValueError("test error")
            entry = {
                "timestamp": "2023-01-01T00:00:00Z",
                "level": "error",
                "package": "test",
                "filename": "test.py",
                "message": "Error",
                "error": error,
            }
            result = format_json(entry)
            parsed = json.loads(result)
            assert parsed["error"]["message"] == "test error"
            assert parsed["error"]["type"] == "ValueError"


class TestLogLevels:
    """Tests for LOG_LEVELS constant."""

    class TestStatementCoverage:
        """Ensure log levels are defined correctly."""

        def test_error_is_lowest(self):
            """ERROR should have lowest priority value."""
            assert LOG_LEVELS["error"] == 0

        def test_warn_priority(self):
            """WARN should have priority 1."""
            assert LOG_LEVELS["warn"] == 1

        def test_info_priority(self):
            """INFO should have priority 2."""
            assert LOG_LEVELS["info"] == 2

        def test_debug_priority(self):
            """DEBUG should have priority 3."""
            assert LOG_LEVELS["debug"] == 3

        def test_trace_is_highest(self):
            """TRACE should have highest priority value."""
            assert LOG_LEVELS["trace"] == 4
