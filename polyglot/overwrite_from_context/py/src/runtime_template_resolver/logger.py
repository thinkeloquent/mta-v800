import os
import sys
from enum import Enum
from typing import Any, Protocol, Optional

class LogLevel(Enum):
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    SILENT = 100

DEFAULT_LOG_LEVEL = LogLevel.DEBUG

class ILogger(Protocol):
    def trace(self, msg: str, *args: Any) -> None: ...
    def debug(self, msg: str, *args: Any) -> None: ...
    def info(self, msg: str, *args: Any) -> None: ...
    def warn(self, msg: str, *args: Any) -> None: ...
    def error(self, msg: str, *args: Any) -> None: ...

class Logger:
    def __init__(self, package_name: str, filename: str, level: Optional[LogLevel] = None):
        self.package = package_name
        self.filename = os.path.basename(filename)
        self.level = level or self._get_env_level()
        self.prefix = f"[{self.package}:{self.filename}]"

    @staticmethod
    def _get_env_level() -> LogLevel:
        env_level = os.environ.get('LOG_LEVEL', 'debug').upper()
        if env_level in LogLevel.__members__:
            return LogLevel[env_level]
        return DEFAULT_LOG_LEVEL

    @classmethod
    def create(cls, package_name: str, filename: str, level: Optional[LogLevel] = None) -> 'Logger':
        return cls(package_name, filename, level=level)

    def _log(self, level: LogLevel, level_name: str, msg: str, *args: Any):
        if self.level.value <= level.value:
            # Simple print for now, can be improved to use logging module or structured logging
            print(f"{self.prefix} {level_name}: {msg}", *args, file=sys.stderr if level.value >= LogLevel.ERROR.value else sys.stdout)

    def trace(self, msg: str, *args: Any):
        self._log(LogLevel.TRACE, "TRACE", msg, *args)

    def debug(self, msg: str, *args: Any):
        self._log(LogLevel.DEBUG, "DEBUG", msg, *args)

    def info(self, msg: str, *args: Any):
        self._log(LogLevel.INFO, "INFO", msg, *args)

    def warn(self, msg: str, *args: Any):
        self._log(LogLevel.WARN, "WARN", msg, *args)

    def error(self, msg: str, *args: Any):
        self._log(LogLevel.ERROR, "ERROR", msg, *args)
