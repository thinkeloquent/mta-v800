# App YAML Static Config - Node.js SDK Guide

The App YAML Static Config SDK provides a high-level API for CLI tools, LLM Agents, and Developer Tools to interact with YAML-based application configuration.

## Installation

```bash
npm install app-yaml-static-config
```

## Usage

### Basic Usage

```typescript
import { AppYamlConfigSDK } from 'app-yaml-static-config';

// Initialize from directory (loads all *.yaml files)
const sdk = await AppYamlConfigSDK.fromDirectory('./config');

// Get configuration values
const appConfig = sdk.get('app');
console.log('App name:', appConfig.name);

// Get nested values
const dbHost = sdk.getNested(['services', 'database', 'host']);
console.log('Database host:', dbHost);

// Get all configuration
const allConfig = sdk.getAll();
console.log('Config keys:', Object.keys(allConfig));
```

### Advanced Initialization

```typescript
import { AppYamlConfig, AppYamlConfigSDK, createLogger } from 'app-yaml-static-config';
import * as path from 'path';

// Create custom logger
const logger = createLogger('my-app', 'config.ts');

// Initialize with specific files
await AppYamlConfig.initialize({
    files: [
        path.join('./config', 'base.yaml'),
        path.join('./config', 'secrets.yaml'),
        path.join('./config', `${process.env.NODE_ENV || 'development'}.yaml`)
    ],
    configDir: './config',
    appEnv: process.env.NODE_ENV,
    logger
});

const config = AppYamlConfig.getInstance();
const sdk = new AppYamlConfigSDK(config);
```

### Using Core API

```typescript
import { AppYamlConfig } from 'app-yaml-static-config';
import * as path from 'path';

// Initialize
await AppYamlConfig.initialize({
    files: [path.join('./config', 'base.yaml')],
    configDir: './config'
});
const config = AppYamlConfig.getInstance();

// Access with type generics
const appName = config.getNested<string>(['app', 'name']);
const dbPort = config.getNested<number>(['services', 'database', 'port'], 5432);

// Get original file content (before merge)
const original = config.getOriginal('./config/base.yaml');
```

## Features

- **Configuration Access**: `get`, `getNested`, `getAll`
- **Resource Discovery**: `listProviders`, `listServices`, `listStorages`
- **Immutability**: Configuration cannot be modified after initialization
- **Deep Merge**: Multiple YAML files are merged with later files overriding earlier ones
- **Safe Access**: All values are deep-cloned via JSON serialization
- **Type Safety**: Generic methods support TypeScript type inference

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
    maxTokens: 4096
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
  retryCount: 3
```

## Error Handling

```typescript
import { ImmutabilityError, ConfigurationError, validateConfigKey } from 'app-yaml-static-config';

// Configuration is immutable
try {
    config.set('key', 'value');
} catch (error) {
    if (error instanceof ImmutabilityError) {
        console.error('Cannot modify:', error.message);
    }
}

// Invalid key
try {
    validateConfigKey('');
} catch (error) {
    if (error instanceof ConfigurationError) {
        console.error('Invalid key:', error.message);
    }
}
```

## Singleton Pattern

The configuration uses a singleton pattern:

```typescript
// First initialization
await AppYamlConfig.initialize(options);

// Subsequent calls return the same instance
const config1 = AppYamlConfig.getInstance();
const config2 = AppYamlConfig.getInstance();
console.log(config1 === config2); // true

// Attempting to re-initialize returns existing instance
await AppYamlConfig.initialize(options); // Returns existing instance
```

## Testing

For testing, reset the singleton between tests:

```typescript
import { describe, it, beforeEach, afterEach } from 'vitest';
import { AppYamlConfig } from 'app-yaml-static-config';

function resetSingleton() {
    // Access private static property (for testing only)
    (AppYamlConfig as any)._instance = null;
}

describe('Config Tests', () => {
    beforeEach(() => {
        resetSingleton();
    });

    afterEach(() => {
        resetSingleton();
    });

    it('should load configuration', async () => {
        await AppYamlConfig.initialize({
            files: ['./test/fixtures/base.yaml'],
            configDir: './test/fixtures'
        });

        const config = AppYamlConfig.getInstance();
        expect(config.get('app')).toBeDefined();
    });
});
```

## TypeScript Support

The SDK includes full TypeScript support with generic methods:

```typescript
interface AppConfig {
    name: string;
    version: string;
}

interface DatabaseConfig {
    host: string;
    port: number;
    name: string;
}

// Typed access
const app = config.get<AppConfig>('app');
const dbHost = config.getNested<string>(['services', 'database', 'host']);
```
