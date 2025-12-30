import logging
from enum import IntEnum
from typing import Protocol, Any

class LogLevel(IntEnum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    NONE = 4

class IVaultFileLogger(Protocol):
    def debug(self, message: str, *args: Any): ...
    def info(self, message: str, *args: Any): ...
    def warn(self, message: str, *args: Any): ...
    def error(self, message: str, *args: Any): ...

class Logger:
    def __init__(self, package_name: str, filename: str):
        self.context = f"[{package_name}:{filename}]"
        self._logger = logging.getLogger("vault_file")
        # Ensure handler exists
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    @staticmethod
    def create(package_name: str, filename: str) -> "IVaultFileLogger":
        return Logger(package_name, filename)

    def _format(self, message: str) -> str:
        return f"{self.context} {message}"

    def debug(self, message: str, *args: Any):
        if _current_log_level <= LogLevel.DEBUG:
            self._logger.debug(self._format(message), *args)

    def info(self, message: str, *args: Any):
        if _current_log_level <= LogLevel.INFO:
            self._logger.info(self._format(message), *args)

    def warn(self, message: str, *args: Any):
        if _current_log_level <= LogLevel.WARN:
            self._logger.warning(self._format(message), *args)

    def error(self, message: str, *args: Any):
        if _current_log_level <= LogLevel.ERROR:
            self._logger.error(self._format(message), *args)

# Global level state
_current_log_level = LogLevel.INFO

def set_log_level(level: LogLevel):
    global _current_log_level
    _current_log_level = level
    logging.getLogger("vault_file").setLevel(logging.DEBUG if level == LogLevel.DEBUG else logging.INFO)

_default_logger = Logger.create("vault_file", "default")

def get_logger() -> IVaultFileLogger:
    return _default_logger

