from typing import Optional
from .interfaces import MissingStrategy
from .errors import MissingValueError

def handle_missing(key: str, strategy: MissingStrategy = MissingStrategy.EMPTY, default_value: Optional[str] = None) -> str:
    if strategy == MissingStrategy.KEEP:
        return f"{{{{{key}}}}}"
    elif strategy == MissingStrategy.ERROR:
        raise MissingValueError(f"Missing value for placeholder: {key}")
    elif strategy == MissingStrategy.DEFAULT:
        return default_value if default_value is not None else ""
    else: # EMPTY
        return ""
