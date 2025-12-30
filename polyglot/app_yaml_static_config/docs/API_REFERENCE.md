# App YAML Static Config API Reference

## Core Components

### InitOptions

Configuration options for initializing the YAML configuration loader.

**TypeScript**
```typescript
interface InitOptions {
    files: string[];
    configDir: string;
    appEnv?: string;
    logger?: ILogger;
}
```

**Python**
```python
class InitOptions:
    def __init__(self,
                 files: List[str],
                 config_dir: str,
                 app_env: Optional[str] = None,
                 logger: Optional[ILogger] = None): ...
```

### ILogger

Logger interface for configuration operations.

**TypeScript**
```typescript
interface ILogger {
    info(message: string, ...args: unknown[]): void;
    warn(message: string, ...args: unknown[]): void;
    error(message: string, ...args: unknown[]): void;
    debug(message: string, ...args: unknown[]): void;
    trace(message: string, ...args: unknown[]): void;
}
```

**Python**
```python
class ILogger(Protocol):
    def info(self, message: str, *args: Any) -> None: ...
    def warn(self, message: str, *args: Any) -> None: ...
    def error(self, message: str, *args: Any) -> None: ...
    def debug(self, message: str, *args: Any) -> None: ...
    def trace(self, message: str, *args: Any) -> None: ...
```

### AppYamlConfig

Singleton class for managing YAML-based static configuration. Provides immutable access to merged configuration from multiple YAML files.

**TypeScript**
```typescript
class AppYamlConfig {
    static initialize(options: InitOptions): Promise<AppYamlConfig>;
    static getInstance(): AppYamlConfig;

    get<T>(key: string, defaultValue?: T): T | undefined;
    getNested<T>(keys: string[], defaultValue?: T): T | undefined;
    getAll(): Record<string, any>;
    getOriginal(file?: string): Record<string, any> | undefined;
    getOriginalAll(): Map<string, Record<string, any>>;
    restore(): void;

    // Immutability stubs (throw ImmutabilityError)
    set(key: string, value: any): never;
    update(updates: Record<string, any>): never;
    reset(): never;
    clear(): never;
}
```

**Python**
```python
class AppYamlConfig:
    @classmethod
    def initialize(cls, options: InitOptions) -> 'AppYamlConfig': ...

    @classmethod
    def get_instance(cls) -> 'AppYamlConfig': ...

    def get(self, key: str, default: Any = None) -> Any: ...
    def get_nested(self, *keys: str, default: Any = None) -> Any: ...
    def get_all(self) -> Dict[str, Any]: ...
    def get_original(self, file: Optional[str] = None) -> Dict[str, Any]: ...
    def get_original_all(self) -> Dict[str, Dict[str, Any]]: ...
    def restore(self) -> None: ...

    # Immutability stubs (raise ImmutabilityError)
    def set(self, key: str, value: Any) -> None: ...
    def update(self, updates: Dict[str, Any]) -> None: ...
    def reset(self) -> None: ...
    def clear(self) -> None: ...
```

### ConfigurationError

Base exception for configuration errors.

**TypeScript**
```typescript
class ConfigurationError extends Error {
    constructor(message: string, context?: unknown);
    readonly context?: unknown;
}
```

**Python**
```python
class ConfigurationError(Exception):
    def __init__(self, message: str, context: Any = None): ...
    context: Any
```

### ImmutabilityError

Exception thrown when attempting to modify an immutable configuration.

**TypeScript**
```typescript
class ImmutabilityError extends ConfigurationError {
    constructor(message: string, context?: unknown);
}
```

**Python**
```python
class ImmutabilityError(ConfigurationError):
    pass
```

## SDK

### AppYamlConfigSDK

High-level SDK providing simplified access to configuration data with JSON serialization for safe value retrieval.

**TypeScript**
```typescript
class AppYamlConfigSDK {
    constructor(config: AppYamlConfig);

    static fromDirectory(configDir: string): Promise<AppYamlConfigSDK>;

    get(key: string): unknown;
    getNested(keys: string[]): unknown;
    getAll(): Record<string, unknown>;
    listProviders(): string[];
    listServices(): string[];
    listStorages(): string[];
}
```

**Python**
```python
class AppYamlConfigSDK:
    def __init__(self, config: AppYamlConfig): ...

    @classmethod
    def from_directory(cls, config_dir: str) -> 'AppYamlConfigSDK': ...

    def get(self, key: str) -> Any: ...
    def get_nested(self, keys: List[str]) -> Any: ...
    def get_all(self) -> Dict[str, Any]: ...
    def list_providers(self) -> List[str]: ...
    def list_services(self) -> List[str]: ...
    def list_storages(self) -> List[str]: ...
```

### SDK Operations

- `get(key)`: Get a top-level configuration value by key
- `getNested(keys)` / `get_nested(keys)`: Get a nested configuration value using a list of keys
- `getAll()` / `get_all()`: Get all configuration values as a dictionary
- `listProviders()` / `list_providers()`: List all provider keys from `providers` section
- `listServices()` / `list_services()`: List all service keys from `services` section
- `listStorages()` / `list_storages()`: List all storage keys from `storages` section

## Utility Functions

### createLogger / create

Factory function to create a prefixed logger instance.

**TypeScript**
```typescript
function create(packageName: string, filename: string): ILogger;
```

**Python**
```python
def create(package_name: str, filename: str) -> ILogger: ...
```

### validateConfigKey / validate_config_key

Validates that a configuration key is not empty.

**TypeScript**
```typescript
function validateConfigKey(key: string): void;
```

**Python**
```python
def validate_config_key(key: str) -> None: ...
```
