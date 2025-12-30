"""
Unit tests for app_yaml_static_config.logger module.

Tests cover:
- Logger factory function
- Logger method calls
- Prefix formatting
"""
import pytest
from io import StringIO
import sys

from app_yaml_static_config.logger import create


class TestLoggerCreate:
    """Tests for logger.create() factory function."""

    class TestStatementCoverage:
        """Ensure every statement executes."""

        def test_create_returns_logger_instance(self):
            """create() should return a logger object."""
            logger = create("test_package", "test_file.py")

            assert logger is not None
            assert hasattr(logger, "info")
            assert hasattr(logger, "warn")
            assert hasattr(logger, "error")
            assert hasattr(logger, "debug")
            assert hasattr(logger, "trace")

        def test_logger_info_method_callable(self, capsys):
            """Logger info method should be callable."""
            logger = create("test_package", "test_file.py")

            logger.info("Test info message")

            captured = capsys.readouterr()
            assert "INFO" in captured.out
            assert "Test info message" in captured.out

        def test_logger_warn_method_callable(self, capsys):
            """Logger warn method should be callable."""
            logger = create("test_package", "test_file.py")

            logger.warn("Test warn message")

            captured = capsys.readouterr()
            assert "WARN" in captured.out
            assert "Test warn message" in captured.out

        def test_logger_error_method_callable(self, capsys):
            """Logger error method should be callable."""
            logger = create("test_package", "test_file.py")

            logger.error("Test error message")

            captured = capsys.readouterr()
            assert "ERROR" in captured.out
            assert "Test error message" in captured.out

        def test_logger_debug_method_callable(self, capsys):
            """Logger debug method should be callable."""
            logger = create("test_package", "test_file.py")

            logger.debug("Test debug message")

            captured = capsys.readouterr()
            assert "DEBUG" in captured.out
            assert "Test debug message" in captured.out

        def test_logger_trace_method_callable(self, capsys):
            """Logger trace method should be callable."""
            logger = create("test_package", "test_file.py")

            logger.trace("Test trace message")

            captured = capsys.readouterr()
            assert "TRACE" in captured.out
            assert "Test trace message" in captured.out

    class TestBranchCoverage:
        """Test all branches."""

        def test_logger_includes_package_name_prefix(self, capsys):
            """Logger output should include package name prefix."""
            logger = create("my_package", "my_file.py")

            logger.info("Test message")

            captured = capsys.readouterr()
            assert "[my_package:my_file.py]" in captured.out

        def test_logger_with_additional_args(self, capsys):
            """Logger should handle additional arguments."""
            logger = create("test_package", "test_file.py")

            logger.info("Message with args", {"key": "value"})

            captured = capsys.readouterr()
            assert "Message with args" in captured.out

    class TestIntegration:
        """Integration tests."""

        def test_multiple_loggers_independent(self, capsys):
            """Multiple loggers should be independent."""
            logger1 = create("package1", "file1.py")
            logger2 = create("package2", "file2.py")

            logger1.info("Message 1")
            logger2.info("Message 2")

            captured = capsys.readouterr()
            assert "[package1:file1.py]" in captured.out
            assert "[package2:file2.py]" in captured.out
