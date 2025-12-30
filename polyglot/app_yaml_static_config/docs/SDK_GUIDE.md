# App YAML Static Config SDK Guide

The App YAML Static Config SDK provides a high-level API for CLI tools, LLM Agents, and Developer Tools to interact with YAML-based application configuration. It offers immutable, type-safe access to merged configuration from multiple YAML files.

## Usage

### Node.js

```typescript
import { AppYamlConfigSDK, AppYamlConfig } from 'app-yaml-static-config';

// Option 1: Initialize from directory
const sdk = await AppYamlConfigSDK.fromDirectory('./config');

// Option 2: Initialize with custom options
await AppYamlConfig.initialize({
    files: ['./config/base.yaml', './config/override.yaml'],
    configDir: './config'
});
const config = AppYamlConfig.getInstance();
const sdk = new AppYamlConfigSDK(config);

// Get configuration values
const appName = sdk.get('app');
console.log('App:', appName);

// Get nested values
const dbHost = sdk.getNested(['services', 'database', 'host']);
console.log('Database host:', dbHost);

// List providers, services, storages
const providers = sdk.listProviders();
console.log('Providers:', providers);
```

### Python

```python
from app_yaml_static_config import AppYamlConfigSDK, AppYamlConfig
from app_yaml_static_config.types import InitOptions

# Option 1: Initialize from directory
sdk = AppYamlConfigSDK.from_directory('./config')

# Option 2: Initialize with custom options
options = InitOptions(
    files=['./config/base.yaml', './config/override.yaml'],
    config_dir='./config'
)
AppYamlConfig.initialize(options)
config = AppYamlConfig.get_instance()
sdk = AppYamlConfigSDK(config)

# Get configuration values
app_name = sdk.get('app')
print(f"App: {app_name}")

# Get nested values
db_host = sdk.get_nested(['services', 'database', 'host'])
print(f"Database host: {db_host}")

# List providers, services, storages
providers = sdk.list_providers()
print(f"Providers: {providers}")
```

## Features

- **Configuration Access**: `get`, `getNested`/`get_nested`, `getAll`/`get_all`
- **Resource Discovery**: `listProviders`/`list_providers`, `listServices`/`list_services`, `listStorages`/`list_storages`
- **Immutability**: Configuration cannot be modified after initialization
- **Deep Merge**: Multiple YAML files are merged with later files overriding earlier ones
- **Safe Access**: All values are deep-cloned to prevent accidental mutation

## Configuration Structure

The SDK expects YAML configuration files with the following optional sections:

```yaml
app:
  name: my-app
  version: 1.0.0

providers:
  anthropic:
    model: claude-3-opus
  openai:
    model: gpt-4

services:
  database:
    host: localhost
    port: 5432
  cache:
    host: localhost
    port: 6379

storages:
  local:
    path: /tmp/storage
  s3:
    bucket: my-bucket
```

## Error Handling

The SDK throws/raises `ImmutabilityError` when attempting to modify configuration:

### Node.js

```typescript
try {
    config.set('key', 'value');
} catch (error) {
    if (error instanceof ImmutabilityError) {
        console.error('Cannot modify immutable configuration');
    }
}
```

### Python

```python
from app_yaml_static_config.validators import ImmutabilityError

try:
    config.set('key', 'value')
except ImmutabilityError:
    print('Cannot modify immutable configuration')
```
