from typing import Protocol, Any, Dict, List, Optional, Union

from .options import ComputeScope, MissingStrategy, ResolverOptions

class ILogger(Protocol):
    def trace(self, msg: str, *args: Any) -> None: ...
    def debug(self, msg: str, *args: Any) -> None: ...
    def info(self, msg: str, *args: Any) -> None: ...
    def warn(self, msg: str, *args: Any) -> None: ...
    def error(self, msg: str, *args: Any) -> None: ...

# Re-export key types for consumers
__all__ = [
    "ILogger",
    "ResolverOptions",
    "ComputeScope",
    "MissingStrategy"
]
