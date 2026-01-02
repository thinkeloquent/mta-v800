# app_yaml_overwrites API Reference

This document provides the complete API reference for the `app_yaml_overwrites` package, showing type signatures and interfaces for both TypeScript and Python implementations.

## Core Components

### Logger

A standardized JSON logger with structured output and log level control via the `LOG_LEVEL` environment variable.

**TypeScript**
```typescript
class Logger {
    private package: string;
    private filename: string;
    private level: string;

    static create(packageName: string, filename: string): Logger;

    debug(message: string, data?: Record<string, any>): void;
    info(message: string, data?: Record<string, any>): void;
    warn(message: string, data?: Record<string, any>): void;
    error(message: string, data?: Record<string, any>): void;
}
```

**Python**
```python
class Logger:
    LEVELS: Dict[str, int] = {
        'trace': 5, 'debug': 10, 'info': 20, 'warn': 30, 'error': 40
    }

    @classmethod
    def create(cls, package_name: str, filename: str) -> 'Logger': ...

    def debug(self, message: str, **kwargs) -> None: ...
    def info(self, message: str, **kwargs) -> None: ...
    def warn(self, message: str, **kwargs) -> None: ...
    def error(self, message: str, **kwargs) -> None: ...
```

---

### ContextBuilder

Builds resolution context for template processing, combining environment, configuration, application state, and custom extenders.

**TypeScript**
```typescript
interface ContextOptions {
    env?: Record<string, string>;
    config?: any;
    app?: any;
    state?: any;
    request?: FastifyRequest;
}

type ContextExtender = (
    currentContext: any,
    request?: FastifyRequest
) => Promise<any> | any;

class ContextBuilder {
    static async build(
        options: ContextOptions,
        extenders?: ContextExtender[]
    ): Promise<any>;
}
```

**Python**
```python
ContextExtender = Callable[
    [Dict[str, Any], Optional[Any]],
    Awaitable[Dict[str, Any]]
]

class ContextBuilder:
    @staticmethod
    async def build(
        options: Dict[str, Any],
        extenders: List[ContextExtender] = None
    ) -> Dict[str, Any]: ...
```

---

### OverwriteMerger

Deep merges configuration overwrites, used for the `overwrite_from_context` pattern.

**TypeScript**
```typescript
function applyOverwrites(
    originalConfig: any,
    overwriteSection: any
): any;
```

**Python**
```python
def apply_overwrites(
    original_config: Dict[str, Any],
    overwrite_section: Dict[str, Any]
) -> Dict[str, Any]: ...
```

---

### ConfigSDK

High-level SDK for managing configuration, including static loading, template resolution, and context building.

**TypeScript**
```typescript
interface ConfigSDKOptions {
    configDir?: string;
    configPath?: string;
    contextExtenders?: ContextExtender[];
    validateSchema?: boolean;
}

class ConfigSDK {
    private static instance: ConfigSDK;

    static async initialize(options?: ConfigSDKOptions): Promise<ConfigSDK>;
    static getInstance(): ConfigSDK;

    getRaw(): any;
    async getResolved(scope: ComputeScope, request?: FastifyRequest): Promise<any>;
    async toJSON(options?: { maskSecrets?: boolean }): Promise<any>;
}
```

**Python**
```python
class ConfigSDK:
    _instance: Optional['ConfigSDK'] = None

    @classmethod
    async def initialize(cls, options: Dict[str, Any] = None) -> 'ConfigSDK': ...

    @classmethod
    def get_instance(cls) -> 'ConfigSDK': ...

    def get_raw(self) -> Dict[str, Any]: ...
    async def get_resolved(self, scope: str, request: Any = None) -> Dict[str, Any]: ...
    async def to_json(self, options: Dict[str, Any] = None) -> Dict[str, Any]: ...
```

---

## SDK

### Initialization

**TypeScript**
```typescript
import { ConfigSDK } from 'app-yaml-overwrites';

// Initialize SDK (singleton)
const sdk = await ConfigSDK.initialize({
    contextExtenders: [authExtender, tenantExtender]
});

// Later access
const instance = ConfigSDK.getInstance();
```

**Python**
```python
from app_yaml_overwrites import ConfigSDK

# Initialize SDK (singleton)
sdk = await ConfigSDK.initialize({
    'context_extenders': [auth_extender, tenant_extender]
})

# Later access
instance = ConfigSDK.get_instance()
```

### SDK Operations

| Operation | Description |
|-----------|-------------|
| `initialize(options)` | Async initialization with options, returns singleton instance |
| `getInstance()` | Get existing instance (throws if not initialized) |
| `getRaw()` | Get raw configuration without resolution |
| `getResolved(scope, request?)` | Get resolved configuration for given scope |
| `toJSON(options?)` | Export configuration as JSON |

---

## Types

### ComputeScope

Defines when template resolution should occur.

**TypeScript**
```typescript
enum ComputeScope {
    STARTUP = 'STARTUP',
    REQUEST = 'REQUEST'
}
```

**Python**
```python
class ComputeScope:
    STARTUP: str = 'STARTUP'
    REQUEST: str = 'REQUEST'
```

### Log Output Format

All loggers output JSON-formatted logs:

```json
{
    "timestamp": "2025-01-02T12:00:00.000Z",
    "level": "INFO",
    "context": "package-name:filename.ts",
    "message": "Log message here",
    "data": { "key": "value" }
}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `debug` | Logging level: `trace`, `debug`, `info`, `warn`, `error` |

---

## See Also

- [SDK Guide](./SDK_GUIDE.md) - High-level usage patterns
- [Server Integration](./SERVER_INTEGRATION.md) - Fastify and FastAPI integration
- [Behavioral Differences](./BEHAVIORAL_DIFFERENCES.md) - Language-specific behaviors
