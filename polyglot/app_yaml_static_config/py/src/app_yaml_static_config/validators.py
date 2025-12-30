from typing import Any

class ConfigurationError(Exception):
    def __init__(self, message: str, context: Any = None):
        self.context = context
        super().__init__(f"{message} (context: {context})")

class ImmutabilityError(ConfigurationError):
    pass

def validate_config_key(key: str) -> None:
    if not key:
        raise ConfigurationError("Config key cannot be empty")
