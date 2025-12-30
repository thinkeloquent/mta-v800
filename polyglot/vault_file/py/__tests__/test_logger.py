"""
Unit tests for vault_file.logger module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
"""
import logging
import pytest

from vault_file.logger import (
    Logger,
    LogLevel,
    IVaultFileLogger,
    set_log_level,
    get_logger,
)


class TestLogger:
    """Tests for Logger class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_create_returns_logger_instance(self):
            """create() should return a logger instance."""
            logger = Logger.create("test_package", "test_file")
            assert logger is not None

        def test_logger_formats_context(self):
            """Logger should format context correctly."""
            logger = Logger("my_package", "my_file")
            formatted = logger._format("test message")
            assert "[my_package:my_file]" in formatted
            assert "test message" in formatted

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test log level filtering branches."""

        def test_debug_logged_at_debug_level(self, caplog):
            """Debug messages should be logged at DEBUG level."""
            set_log_level(LogLevel.DEBUG)
            logger = Logger.create("test", "debug_test")

            with caplog.at_level(logging.DEBUG, logger="vault_file"):
                logger.debug("debug message")

            assert any("debug message" in r.message for r in caplog.records)

        def test_debug_not_logged_at_info_level(self, caplog):
            """Debug messages should not be logged at INFO level."""
            set_log_level(LogLevel.INFO)
            logger = Logger.create("test", "info_test")

            with caplog.at_level(logging.DEBUG, logger="vault_file"):
                logger.debug("should not appear")

            # Check that no record contains our debug message
            debug_records = [r for r in caplog.records if "should not appear" in r.message]
            assert len(debug_records) == 0

        def test_info_logged_at_info_level(self, caplog):
            """Info messages should be logged at INFO level."""
            set_log_level(LogLevel.INFO)
            logger = Logger.create("test", "info_test")

            with caplog.at_level(logging.INFO, logger="vault_file"):
                logger.info("info message")

            assert any("info message" in r.message for r in caplog.records)

        def test_warn_logged_at_warn_level(self, caplog):
            """Warn messages should be logged at WARN level."""
            set_log_level(LogLevel.WARN)
            logger = Logger.create("test", "warn_test")

            with caplog.at_level(logging.WARNING, logger="vault_file"):
                logger.warn("warn message")

            assert any("warn message" in r.message for r in caplog.records)

        def test_error_logged_at_error_level(self, caplog):
            """Error messages should be logged at ERROR level."""
            set_log_level(LogLevel.ERROR)
            logger = Logger.create("test", "error_test")

            with caplog.at_level(logging.ERROR, logger="vault_file"):
                logger.error("error message")

            assert any("error message" in r.message for r in caplog.records)

        def test_nothing_logged_at_none_level(self, caplog):
            """Nothing should be logged at NONE level."""
            set_log_level(LogLevel.NONE)
            logger = Logger.create("test", "none_test")

            with caplog.at_level(logging.DEBUG, logger="vault_file"):
                logger.debug("debug")
                logger.info("info")
                logger.warn("warn")
                logger.error("error")

            # Filter only our test messages
            our_messages = [r for r in caplog.records if any(
                msg in r.message for msg in ["debug", "info", "warn", "error"]
            )]
            assert len(our_messages) == 0

            # Reset for other tests
            set_log_level(LogLevel.INFO)


class TestLogLevel:
    """Tests for LogLevel enum."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure all log levels are defined."""

        def test_debug_level_value(self):
            """DEBUG should have value 0."""
            assert LogLevel.DEBUG == 0

        def test_info_level_value(self):
            """INFO should have value 1."""
            assert LogLevel.INFO == 1

        def test_warn_level_value(self):
            """WARN should have value 2."""
            assert LogLevel.WARN == 2

        def test_error_level_value(self):
            """ERROR should have value 3."""
            assert LogLevel.ERROR == 3

        def test_none_level_value(self):
            """NONE should have value 4."""
            assert LogLevel.NONE == 4

    # =========================================================================
    # Comparison
    # =========================================================================

    class TestComparison:
        """Test log level comparisons."""

        def test_debug_less_than_info(self):
            """DEBUG should be less than INFO."""
            assert LogLevel.DEBUG < LogLevel.INFO

        def test_info_less_than_warn(self):
            """INFO should be less than WARN."""
            assert LogLevel.INFO < LogLevel.WARN

        def test_warn_less_than_error(self):
            """WARN should be less than ERROR."""
            assert LogLevel.WARN < LogLevel.ERROR

        def test_error_less_than_none(self):
            """ERROR should be less than NONE."""
            assert LogLevel.ERROR < LogLevel.NONE


class TestSetLogLevel:
    """Tests for set_log_level function."""

    def test_set_to_debug(self):
        """Setting to DEBUG should enable all logs."""
        set_log_level(LogLevel.DEBUG)
        # Just verify no exception
        logger = Logger.create("test", "test")
        logger.debug("test")

    def test_set_to_none(self):
        """Setting to NONE should disable all logs."""
        set_log_level(LogLevel.NONE)
        # Just verify no exception
        logger = Logger.create("test", "test")
        logger.error("test")

        # Reset
        set_log_level(LogLevel.INFO)


class TestGetLogger:
    """Tests for get_logger function."""

    def test_returns_default_logger(self):
        """get_logger should return the default logger."""
        logger = get_logger()
        assert logger is not None

    def test_returns_same_instance(self):
        """get_logger should return the same instance."""
        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2


class TestIVaultFileLogger:
    """Tests for IVaultFileLogger protocol."""

    def test_logger_implements_protocol(self):
        """Logger should implement IVaultFileLogger protocol."""
        logger = Logger.create("test", "test")

        # Verify all required methods exist
        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warn")
        assert hasattr(logger, "error")
        assert callable(logger.debug)
        assert callable(logger.info)
        assert callable(logger.warn)
        assert callable(logger.error)
