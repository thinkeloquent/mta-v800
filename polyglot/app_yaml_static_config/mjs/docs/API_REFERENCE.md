# App YAML Static Config - Node.js API Reference

## Core Components

### InitOptions

Configuration options for initializing the YAML configuration loader.

```typescript
interface InitOptions {
    files: string[];
    configDir: string;
    appEnv?: string;
    logger?: ILogger;
}
```

**Properties:**
- `files`: Array of YAML file paths to load and merge
- `configDir`: Base directory for configuration files
- `appEnv`: Optional environment name (e.g., "development", "production")
- `logger`: Optional custom logger implementing `ILogger` interface

### ILogger

Logger interface for configuration operations.

```typescript
interface ILogger {
    info(message: string, ...args: unknown[]): void;
    warn(message: string, ...args: unknown[]): void;
    error(message: string, ...args: unknown[]): void;
    debug(message: string, ...args: unknown[]): void;
    trace(message: string, ...args: unknown[]): void;
}
```

### AppYamlConfig

Singleton class for managing YAML-based static configuration.

```typescript
class AppYamlConfig {
    /**
     * Initialize the singleton with configuration options.
     */
    static async initialize(options: InitOptions): Promise<AppYamlConfig>;

    /**
     * Get the singleton instance. Throws if not initialized.
     */
    static getInstance(): AppYamlConfig;

    /**
     * Get a top-level configuration value.
     */
    get<T>(key: string, defaultValue?: T): T | undefined;

    /**
     * Get a nested configuration value using an array of keys.
     */
    getNested<T>(keys: string[], defaultValue?: T): T | undefined;

    /**
     * Get a deep copy of all configuration.
     */
    getAll(): Record<string, any>;

    /**
     * Get original config from a specific file.
     */
    getOriginal(file?: string): Record<string, any> | undefined;

    /**
     * Get all original configs keyed by file path.
     */
    getOriginalAll(): Map<string, Record<string, any>>;

    /**
     * Restore configuration to initial merged state.
     */
    restore(): void;

    // Immutability stubs - all throw ImmutabilityError
    set(key: string, value: any): never;
    update(updates: Record<string, any>): never;
    reset(): never;
    clear(): never;
}
```

### ConfigurationError

Base error class for configuration errors.

```typescript
class ConfigurationError extends Error {
    constructor(message: string, context?: unknown);
    readonly context?: unknown;
}
```

### ImmutabilityError

Error thrown when attempting to modify immutable configuration.

```typescript
class ImmutabilityError extends ConfigurationError {
    constructor(message: string, context?: unknown);
}
```

## SDK

### AppYamlConfigSDK

High-level SDK for simplified configuration access.

```typescript
class AppYamlConfigSDK {
    constructor(config: AppYamlConfig);

    /**
     * Create SDK from all YAML files in a directory.
     */
    static async fromDirectory(configDir: string): Promise<AppYamlConfigSDK>;

    /**
     * Get a top-level configuration value (JSON-safe copy).
     */
    get(key: string): unknown;

    /**
     * Get a nested value using an array of keys (JSON-safe copy).
     */
    getNested(keys: string[]): unknown;

    /**
     * Get all configuration (JSON-safe copy).
     */
    getAll(): Record<string, unknown>;

    /**
     * List all provider keys from 'providers' section.
     */
    listProviders(): string[];

    /**
     * List all service keys from 'services' section.
     */
    listServices(): string[];

    /**
     * List all storage keys from 'storages' section.
     */
    listStorages(): string[];
}
```

## Utility Functions

### create (createLogger)

Factory function to create a prefixed logger instance.

```typescript
import { createLogger } from 'app-yaml-static-config';

function create(packageName: string, filename: string): ILogger;
```

### validateConfigKey

Validates that a configuration key is not empty.

```typescript
import { validateConfigKey } from 'app-yaml-static-config';

function validateConfigKey(key: string): void;
```

## Exports

```typescript
// index.ts exports
export { AppYamlConfig } from './core.js';
export { InitOptions, ILogger, LoadResult } from './types.js';
export { AppYamlConfigSDK } from './sdk.js';
export { create as createLogger } from './logger.js';
export { ConfigurationError, ImmutabilityError, validateConfigKey } from './validators.js';
```

## Usage Example

```typescript
import { AppYamlConfig, AppYamlConfigSDK } from 'app-yaml-static-config';
import * as path from 'path';

// Initialize configuration
await AppYamlConfig.initialize({
    files: [
        path.join('./config', 'base.yaml'),
        path.join('./config', 'production.yaml')
    ],
    configDir: './config'
});

// Get instance and create SDK
const config = AppYamlConfig.getInstance();
const sdk = new AppYamlConfigSDK(config);

// Access configuration
const appName = config.getNested<string>(['app', 'name']);
const dbConfig = sdk.get('services');
const providers = sdk.listProviders();

console.log('App:', appName);
console.log('Providers:', providers);
```
