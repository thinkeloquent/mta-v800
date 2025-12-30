# App YAML Static Config - Python SDK Guide

The App YAML Static Config SDK provides a high-level API for CLI tools, LLM Agents, and Developer Tools to interact with YAML-based application configuration.

## Installation

```bash
pip install app-yaml-static-config
```

## Usage

### Basic Usage

```python
from app_yaml_static_config import AppYamlConfigSDK

# Initialize from directory (loads all *.yaml files)
sdk = AppYamlConfigSDK.from_directory('./config')

# Get configuration values
app_config = sdk.get('app')
print(f"App name: {app_config['name']}")

# Get nested values
db_host = sdk.get_nested(['services', 'database', 'host'])
print(f"Database host: {db_host}")

# Get all configuration
all_config = sdk.get_all()
print(f"Config keys: {list(all_config.keys())}")
```

### Advanced Initialization

```python
from app_yaml_static_config import AppYamlConfig, AppYamlConfigSDK
from app_yaml_static_config.types import InitOptions
from app_yaml_static_config.logger import create

# Create custom logger
logger = create('my-app', 'config.py')

# Initialize with specific files
options = InitOptions(
    files=[
        './config/base.yaml',
        './config/secrets.yaml',
        f'./config/{os.getenv("APP_ENV", "development")}.yaml'
    ],
    config_dir='./config',
    app_env=os.getenv('APP_ENV'),
    logger=logger
)

AppYamlConfig.initialize(options)
config = AppYamlConfig.get_instance()
sdk = AppYamlConfigSDK(config)
```

### Using Core API

```python
from app_yaml_static_config import AppYamlConfig
from app_yaml_static_config.types import InitOptions

# Initialize
options = InitOptions(
    files=['./config/base.yaml'],
    config_dir='./config'
)
AppYamlConfig.initialize(options)
config = AppYamlConfig.get_instance()

# Access with variadic keys (core API)
app_name = config.get_nested('app', 'name')
db_port = config.get_nested('services', 'database', 'port', default=5432)

# Get original file content (before merge)
original = config.get_original('./config/base.yaml')
```

## Features

- **Configuration Access**: `get`, `get_nested`, `get_all`
- **Resource Discovery**: `list_providers`, `list_services`, `list_storages`
- **Immutability**: Configuration cannot be modified after initialization
- **Deep Merge**: Multiple YAML files are merged with later files overriding earlier ones
- **Safe Access**: All values are deep-cloned via JSON serialization

## Configuration Structure

Example YAML configuration:

```yaml
# config/base.yaml
app:
  name: my-app
  version: 1.0.0
  debug: false

providers:
  anthropic:
    model: claude-3-opus
    max_tokens: 4096
  openai:
    model: gpt-4

services:
  database:
    host: localhost
    port: 5432
    name: mydb
  cache:
    host: localhost
    port: 6379

storages:
  local:
    path: /tmp/storage
  s3:
    bucket: my-bucket
    region: us-east-1

global:
  timeout: 30000
  retry_count: 3
```

## Error Handling

```python
from app_yaml_static_config.validators import ImmutabilityError, ConfigurationError

# Configuration is immutable
try:
    config.set('key', 'value')
except ImmutabilityError as e:
    print(f"Cannot modify: {e}")

# Invalid key
try:
    validate_config_key('')
except ConfigurationError as e:
    print(f"Invalid key: {e}")
```

## Singleton Pattern

The configuration uses a singleton pattern:

```python
# First initialization
AppYamlConfig.initialize(options)

# Subsequent calls return the same instance
config1 = AppYamlConfig.get_instance()
config2 = AppYamlConfig.get_instance()
assert config1 is config2  # Same instance

# Attempting to re-initialize raises an error
AppYamlConfig.initialize(options)  # Raises Exception
```

## Testing

For testing, reset the singleton between tests:

```python
import pytest
from app_yaml_static_config.core import AppYamlConfig

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton before each test."""
    AppYamlConfig._instance = None
    AppYamlConfig._config = {}
    AppYamlConfig._original_configs = {}
    AppYamlConfig._initial_merged_config = None
    yield
    AppYamlConfig._instance = None
```
