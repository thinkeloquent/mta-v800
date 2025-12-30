from typing import Any
from .types import ILogger

def create(package_name: str, filename: str) -> ILogger:
    prefix = f"[{package_name}:{filename}]"

    class Logger:
        def info(self, msg: str, *args: Any) -> None:
            print(f"{prefix} INFO: {msg}", *args)
        def warn(self, msg: str, *args: Any) -> None:
            print(f"{prefix} WARN: {msg}", *args)
        def error(self, msg: str, *args: Any) -> None:
            print(f"{prefix} ERROR: {msg}", *args)
        def debug(self, msg: str, *args: Any) -> None:
            print(f"{prefix} DEBUG: {msg}", *args)
        def trace(self, msg: str, *args: Any) -> None:
            print(f"{prefix} TRACE: {msg}", *args)

    return Logger()
