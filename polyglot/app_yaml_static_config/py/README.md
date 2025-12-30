# app_yaml_static_config

Polyglot YAML Configuration Loading, Storage, and Retrieval for Python.

## Installation

```bash
poetry install
```

## Usage

```python
from app_yaml_static_config import AppYamlConfig, AppYamlConfigSDK
from app_yaml_static_config.types import InitOptions

# Initialize configuration
options = InitOptions(
    files=["config.yaml"],
    config_dir="./config"
)
config = AppYamlConfig.initialize(options)

# Access configuration
app_name = config.get_nested("app", "name")
all_config = config.get_all()

# Using SDK for external tools
sdk = AppYamlConfigSDK.from_directory("./config")
providers = sdk.list_providers()
```

## Testing

```bash
poetry run pytest
```
