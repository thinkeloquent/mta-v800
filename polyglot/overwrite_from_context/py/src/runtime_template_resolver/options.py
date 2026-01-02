from enum import Enum
from dataclasses import dataclass
from typing import Optional
# Avoid circular import if possible. Logger is used for type hint.
# We can use string forward reference or TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logger import Logger

class ComputeScope(Enum):
    STARTUP = "STARTUP"
    REQUEST = "REQUEST"

class MissingStrategy(Enum):
    ERROR = "ERROR"
    DEFAULT = "DEFAULT"
    IGNORE = "IGNORE"

@dataclass
class ResolverOptions:
    max_depth: int = 10
    missing_strategy: MissingStrategy = MissingStrategy.ERROR
    logger: Optional['Logger'] = None
