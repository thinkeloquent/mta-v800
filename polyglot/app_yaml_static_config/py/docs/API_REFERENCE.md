# App YAML Static Config - Python API Reference

## Core Components

### InitOptions

Configuration options for initializing the YAML configuration loader.

```python
from app_yaml_static_config.types import InitOptions, ILogger
from typing import List, Optional

class InitOptions:
    def __init__(self,
                 files: List[str],
                 config_dir: str,
                 app_env: Optional[str] = None,
                 logger: Optional[ILogger] = None): ...
```

**Parameters:**
- `files`: List of YAML file paths to load and merge
- `config_dir`: Base directory for configuration files
- `app_env`: Optional environment name (e.g., "development", "production")
- `logger`: Optional custom logger implementing `ILogger` protocol

### ILogger

Logger protocol for configuration operations.

```python
from typing import Protocol, Any

class ILogger(Protocol):
    def info(self, message: str, *args: Any) -> None: ...
    def warn(self, message: str, *args: Any) -> None: ...
    def error(self, message: str, *args: Any) -> None: ...
    def debug(self, message: str, *args: Any) -> None: ...
    def trace(self, message: str, *args: Any) -> None: ...
```

### AppYamlConfig

Singleton class for managing YAML-based static configuration.

```python
from typing import Any, Dict, Optional
from app_yaml_static_config.core import AppYamlConfig
from app_yaml_static_config.types import InitOptions

class AppYamlConfig:
    @classmethod
    def initialize(cls, options: InitOptions) -> 'AppYamlConfig':
        """Initialize the singleton with configuration options."""
        ...

    @classmethod
    def get_instance(cls) -> 'AppYamlConfig':
        """Get the singleton instance. Raises if not initialized."""
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Get a top-level configuration value."""
        ...

    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """Get a nested configuration value using variadic keys."""
        ...

    def get_all(self) -> Dict[str, Any]:
        """Get a deep copy of all configuration."""
        ...

    def get_original(self, file: Optional[str] = None) -> Dict[str, Any]:
        """Get original config from a specific file."""
        ...

    def get_original_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all original configs keyed by file path."""
        ...

    def restore(self) -> None:
        """Restore configuration to initial merged state."""
        ...

    # Immutability stubs - all raise ImmutabilityError
    def set(self, key: str, value: Any) -> None: ...
    def update(self, updates: Dict[str, Any]) -> None: ...
    def reset(self) -> None: ...
    def clear(self) -> None: ...
```

### ConfigurationError

Base exception for configuration errors.

```python
from app_yaml_static_config.validators import ConfigurationError

class ConfigurationError(Exception):
    def __init__(self, message: str, context: Any = None): ...
    context: Any
```

### ImmutabilityError

Exception raised when attempting to modify immutable configuration.

```python
from app_yaml_static_config.validators import ImmutabilityError

class ImmutabilityError(ConfigurationError):
    pass
```

## SDK

### AppYamlConfigSDK

High-level SDK for simplified configuration access.

```python
from typing import Any, Dict, List
from app_yaml_static_config.sdk import AppYamlConfigSDK
from app_yaml_static_config.core import AppYamlConfig

class AppYamlConfigSDK:
    def __init__(self, config: AppYamlConfig): ...

    @classmethod
    def from_directory(cls, config_dir: str) -> 'AppYamlConfigSDK':
        """Create SDK from all YAML files in a directory."""
        ...

    def get(self, key: str) -> Any:
        """Get a top-level configuration value (JSON-safe copy)."""
        ...

    def get_nested(self, keys: List[str]) -> Any:
        """Get a nested value using a list of keys (JSON-safe copy)."""
        ...

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration (JSON-safe copy)."""
        ...

    def list_providers(self) -> List[str]:
        """List all provider keys from 'providers' section."""
        ...

    def list_services(self) -> List[str]:
        """List all service keys from 'services' section."""
        ...

    def list_storages(self) -> List[str]:
        """List all storage keys from 'storages' section."""
        ...
```

## Utility Functions

### create

Factory function to create a prefixed logger instance.

```python
from app_yaml_static_config.logger import create

def create(package_name: str, filename: str) -> ILogger:
    """Create a logger with [package_name:filename] prefix."""
    ...
```

### validate_config_key

Validates that a configuration key is not empty.

```python
from app_yaml_static_config.validators import validate_config_key

def validate_config_key(key: str) -> None:
    """Raise ConfigurationError if key is empty."""
    ...
```

## Usage Example

```python
from app_yaml_static_config import AppYamlConfig, AppYamlConfigSDK
from app_yaml_static_config.types import InitOptions

# Initialize configuration
options = InitOptions(
    files=['./config/base.yaml', './config/production.yaml'],
    config_dir='./config'
)
AppYamlConfig.initialize(options)

# Get instance and create SDK
config = AppYamlConfig.get_instance()
sdk = AppYamlConfigSDK(config)

# Access configuration
app_name = config.get_nested('app', 'name')
db_config = sdk.get('services')
providers = sdk.list_providers()
```
