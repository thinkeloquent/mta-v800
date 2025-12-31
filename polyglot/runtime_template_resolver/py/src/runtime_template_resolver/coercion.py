import json
from typing import Any
from .logger import logger

log = logger.create("runtime_template_resolver", __file__)

def to_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value)
        except Exception as e:
            log.warning("Failed to stringify object", error=str(e))
            return str(value)
    return str(value)
