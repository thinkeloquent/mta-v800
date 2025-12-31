from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Union
from enum import Enum
from .logger import LoggerProtocol

class MissingStrategy(str, Enum):
    KEEP = "KEEP"
    EMPTY = "EMPTY"
    ERROR = "ERROR"
    DEFAULT = "DEFAULT"

@dataclass
class ResolverOptions:
    missing_strategy: Optional[MissingStrategy] = None
    throw_on_error: Optional[bool] = None
    logger: Optional[LoggerProtocol] = None

@dataclass
class ResolverResult:
    value: str
    placeholders: List[str] = field(default_factory=list)
    errors: List[Exception] = field(default_factory=list)

class TemplateResolverProtocol(Protocol):
    def resolve(self, template: str, context: Dict[str, Any], options: Optional[ResolverOptions] = None) -> str: ...
    def resolve_object(self, obj: Any, context: Dict[str, Any], options: Optional[ResolverOptions] = None) -> Any: ...
