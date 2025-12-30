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

class ConsoleLogger:
    def __init__(self):
        self.level = LogLevel.INFO
        self._logger = logging.getLogger("vault_file")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    def set_level(self, level: LogLevel):
        self.level = level
        if level == LogLevel.DEBUG:
            self._logger.setLevel(logging.DEBUG)
        elif level == LogLevel.INFO:
            self._logger.setLevel(logging.INFO)
        elif level == LogLevel.WARN:
            self._logger.setLevel(logging.WARNING)
        elif level == LogLevel.ERROR:
            self._logger.setLevel(logging.ERROR)
        elif level == LogLevel.NONE:
            self._logger.setLevel(logging.CRITICAL + 1)

    def debug(self, message: str, *args: Any):
        if self.level <= LogLevel.DEBUG:
            self._logger.debug(message, *args)

    def info(self, message: str, *args: Any):
        if self.level <= LogLevel.INFO:
            self._logger.info(message, *args)

    def warn(self, message: str, *args: Any):
        if self.level <= LogLevel.WARN:
            self._logger.warning(message, *args)

    def error(self, message: str, *args: Any):
        if self.level <= LogLevel.ERROR:
            self._logger.error(message, *args)

_logger_instance = ConsoleLogger()

def get_logger() -> IVaultFileLogger:
    return _logger_instance

def set_log_level(level: LogLevel):
    _logger_instance.set_level(level)
