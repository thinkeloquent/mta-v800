
import os
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any

class Logger:
    LEVELS = {
        'trace': logging.DEBUG - 5,
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR
    }

    def __init__(self, package_name: str, filename: str):
        self._package = package_name
        self._filename = filename
        self._level = os.environ.get('LOG_LEVEL', 'debug').lower()
        self._logger = logging.getLogger(f"{package_name}:{filename}")
        self._logger.setLevel(self.LEVELS.get(self._level, logging.DEBUG))
        
        # Ensure we have a handler for stdout
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            self._logger.addHandler(handler)

    @classmethod
    def create(cls, package_name: str, filename: str) -> 'Logger':
        return cls(package_name, filename)

    def debug(self, message: str, **kwargs):
        self._log('debug', message, kwargs)

    def info(self, message: str, **kwargs):
        self._log('info', message, kwargs)
        
    def warn(self, message: str, **kwargs):
        self._log('warn', message, kwargs)

    def error(self, message: str, **kwargs):
        self._log('error', message, kwargs)

    def _log(self, level: str, message: str, data: Dict[str, Any]):
        if self._logger.isEnabledFor(self.LEVELS[level]):
            entry = {
                "timestamp": datetime.isoformat(datetime.now()),
                "level": level.upper(),
                "context": f"{self._package}:{self._filename}",
                "message": message,
                "data": data
            }
            # Standard Python logger format might interfere, so we just print JSON logic 
            # effectively mimicking the Node logger or letting standard logging handlers handle it.
            # For parity with Node, we use a structured dict passed to logging.
            self._logger.log(self.LEVELS[level], json.dumps(entry))
