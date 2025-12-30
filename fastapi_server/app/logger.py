"""
Logger utility for defensive programming with verbose logging.

Usage:
    from app.logger import logger
    log = logger.create("server", __file__)
    log.info("Server started")
    log.debug("Request received", {"method": "GET", "path": "/"})
    log.error("Failed to connect", error=Exception("Connection refused"))
"""

import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union


# Log levels with numeric priority (lower = more important)
LOG_LEVELS = {
    "error": 0,
    "warn": 1,
    "info": 2,
    "debug": 3,
    "trace": 4,
}

# ANSI color codes for terminal output
COLORS = {
    "reset": "\x1b[0m",
    "red": "\x1b[31m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "cyan": "\x1b[36m",
    "gray": "\x1b[90m",
    "white": "\x1b[37m",
}

LEVEL_COLORS = {
    "error": COLORS["red"],
    "warn": COLORS["yellow"],
    "info": COLORS["blue"],
    "debug": COLORS["cyan"],
    "trace": COLORS["gray"],
}


class LoggerConfig:
    """Default logger configuration."""

    def __init__(
        self,
        level: str = None,
        colorize: bool = None,
        timestamp: bool = True,
        json_format: bool = None,
        output: Optional[Callable[[str], None]] = None,
    ):
        self.level = level or os.getenv("LOG_LEVEL", "debug").lower()
        self.colorize = colorize if colorize is not None else os.getenv("NO_COLOR") != "1"
        self.timestamp = timestamp
        self.json_format = json_format if json_format is not None else os.getenv("LOG_FORMAT") == "json"
        self.output = output


DEFAULT_CONFIG = LoggerConfig()


def extract_filename(filepath: str) -> str:
    """Extract filename from __file__ path."""
    if not filepath:
        return "unknown"
    return Path(filepath).name


def format_human(entry: Dict[str, Any], config: LoggerConfig) -> str:
    """Format a log entry for human-readable output."""
    timestamp = entry.get("timestamp", "")
    level = entry.get("level", "info")
    pkg = entry.get("package", "")
    filename = entry.get("filename", "")
    message = entry.get("message", "")
    data = entry.get("data")
    error = entry.get("error")

    level_color = LEVEL_COLORS.get(level, "") if config.colorize else ""
    reset_color = COLORS["reset"] if config.colorize else ""
    gray_color = COLORS["gray"] if config.colorize else ""
    red_color = COLORS["red"] if config.colorize else ""

    parts = []

    # Timestamp
    if config.timestamp:
        parts.append(f"{gray_color}[{timestamp}]{reset_color}")

    # Level (padded)
    level_str = level.upper().ljust(5)
    parts.append(f"{level_color}{level_str}{reset_color}")

    # Package and filename context
    parts.append(f"{gray_color}[{pkg}:{filename}]{reset_color}")

    # Message
    parts.append(message)

    line = " ".join(parts)

    # Additional data
    if data:
        line += f" {gray_color}{json.dumps(data)}{reset_color}"

    # Error stack
    if error:
        error_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        line += f"\n{red_color}{error_str}{reset_color}"

    return line


def format_json(entry: Dict[str, Any]) -> str:
    """Format a log entry as JSON."""
    output = {**entry}
    if entry.get("error"):
        error = entry["error"]
        output["error"] = {
            "message": str(error),
            "type": type(error).__name__,
            "traceback": "".join(traceback.format_exception(type(error), error, error.__traceback__)),
        }
    return json.dumps(output, default=str)


class Logger:
    """
    Logger instance for a specific package/module.
    Provides a Console/Print-like interface.
    """

    def __init__(
        self,
        package_name: str,
        filename: str,
        config: Optional[LoggerConfig] = None,
    ):
        self.package_name = package_name
        self.filename = extract_filename(filename)
        self.config = config or LoggerConfig()
        self._current_level_priority = LOG_LEVELS.get(self.config.level, LOG_LEVELS["info"])

    def _log_at_level(
        self,
        level: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
    ) -> None:
        """Internal log function."""
        level_priority = LOG_LEVELS.get(level, LOG_LEVELS["info"])

        # Skip if below current log level
        if level_priority > self._current_level_priority:
            return

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "package": self.package_name,
            "filename": self.filename,
            "message": str(message),
        }

        if data:
            entry["data"] = data

        if error:
            entry["error"] = error

        # Format output
        if self.config.json_format:
            formatted = format_json(entry)
        else:
            formatted = format_human(entry, self.config)

        # Write to output
        if self.config.output:
            self.config.output(formatted)
        elif level in ("error", "warn"):
            print(formatted, file=sys.stderr)
        else:
            print(formatted)

    # Standard Console/Print interface methods
    def log(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        """Log at INFO level (alias for info)."""
        self._log_at_level("info", message, data, error)

    def info(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        """Log at INFO level."""
        self._log_at_level("info", message, data, error)

    def warn(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        """Log at WARN level."""
        self._log_at_level("warn", message, data, error)

    def warning(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        """Log at WARN level (alias for warn)."""
        self._log_at_level("warn", message, data, error)

    def error(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        """Log at ERROR level."""
        self._log_at_level("error", message, data, error)

    def debug(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        """Log at DEBUG level."""
        self._log_at_level("debug", message, data, error)

    def trace(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        """Log at TRACE level."""
        self._log_at_level("trace", message, data, error)

    def child(self, child_filename: str, **kwargs) -> "Logger":
        """Create child logger with same package but different filename or config."""
        new_config = LoggerConfig(
            level=kwargs.get("level", self.config.level),
            colorize=kwargs.get("colorize", self.config.colorize),
            timestamp=kwargs.get("timestamp", self.config.timestamp),
            json_format=kwargs.get("json_format", self.config.json_format),
            output=kwargs.get("output", self.config.output),
        )
        return Logger(self.package_name, child_filename, new_config)

    def with_context(self, context: Dict[str, Any]) -> "ContextLogger":
        """Create new logger with additional context merged into data."""
        return ContextLogger(self, context)


class ContextLogger:
    """Logger wrapper that merges context into all log data."""

    def __init__(self, parent: Logger, context: Dict[str, Any]):
        self._parent = parent
        self._context = context

    def _merge_data(self, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        merged = {**self._context}
        if data:
            merged.update(data)
        return merged

    def log(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        self._parent.log(message, self._merge_data(data), error)

    def info(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        self._parent.info(message, self._merge_data(data), error)

    def warn(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        self._parent.warn(message, self._merge_data(data), error)

    def warning(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        self._parent.warning(message, self._merge_data(data), error)

    def error(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        self._parent.error(message, self._merge_data(data), error)

    def debug(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        self._parent.debug(message, self._merge_data(data), error)

    def trace(self, message: str, data: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> None:
        self._parent.trace(message, self._merge_data(data), error)


class LoggerFactory:
    """Factory for creating logger instances."""

    LOG_LEVELS = LOG_LEVELS
    DEFAULT_CONFIG = DEFAULT_CONFIG

    @staticmethod
    def create(
        package_name: str,
        filename: str,
        level: Optional[str] = None,
        colorize: Optional[bool] = None,
        timestamp: bool = True,
        json_format: Optional[bool] = None,
        output: Optional[Callable[[str], None]] = None,
    ) -> Logger:
        """
        Create a logger instance for a specific package/module.

        Args:
            package_name: The name of the package/module
            filename: The filename (use __file__)
            level: Log level (error, warn, info, debug, trace)
            colorize: Enable ANSI colors (default: based on NO_COLOR env)
            timestamp: Include timestamps (default: True)
            json_format: Output as JSON (default: based on LOG_FORMAT env)
            output: Custom output function (default: print to stdout/stderr)

        Returns:
            Logger instance with standard Console/Print interface
        """
        config = LoggerConfig(
            level=level,
            colorize=colorize,
            timestamp=timestamp,
            json_format=json_format,
            output=output,
        )
        return Logger(package_name, filename, config)


# Export the logger factory as default
logger = LoggerFactory()
