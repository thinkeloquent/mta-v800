import os
import json
import sys
import datetime
from typing import Any, Dict, Protocol, Literal

class LoggerProtocol(Protocol):
    def debug(self, message: str, **kwargs: Any) -> None: ...
    def info(self, message: str, **kwargs: Any) -> None: ...
    def warning(self, message: str, **kwargs: Any) -> None: ...
    def error(self, message: str, **kwargs: Any) -> None: ...

LogLevel = Literal["debug", "info", "warn", "error"]

LOG_LEVELS: Dict[LogLevel, int] = {
    "debug": 0,
    "info": 1,
    "warn": 2,
    "error": 3
}

class ConsoleLogger:
    def __init__(self, package_name: str, filename: str, level: LogLevel = "debug"):
        self.package_name = package_name
        self.filename = os.path.basename(filename)
        self.level_name = level
        self.level_value = LOG_LEVELS.get(level, 0)

    def _should_log(self, level: LogLevel) -> bool:
        return LOG_LEVELS.get(level, 0) >= self.level_value

    def _format(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        if not self._should_log(level):
            return

        output = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": level,
            "package": self.package_name,
            "file": self.filename,
            "message": message,
            **kwargs
        }
        print(json.dumps(output), file=sys.stdout)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._format("debug", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._format("info", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._format("warn", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._format("error", message, **kwargs)

class LoggerFactory:
    @staticmethod
    def create(package_name: str, filename: str) -> LoggerProtocol:
        env_level = os.getenv("LOG_LEVEL", "debug").lower()
        # map warning to warn if needed, basic check
        if env_level == "warning": env_level = "warn"
        return ConsoleLogger(package_name, filename, level=env_level) # type: ignore

logger = LoggerFactory()
