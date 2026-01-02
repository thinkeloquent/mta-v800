# app_yaml_overwrites TypeScript API Reference

This document provides the complete TypeScript API reference for the `app_yaml_overwrites` package.

## Installation

```bash
npm install app-yaml-overwrites
# or
pnpm add app-yaml-overwrites
```

## Core Components

### Logger

```typescript
import { Logger } from 'app-yaml-overwrites';

class Logger {
    private package: string;
    private filename: string;
    private level: string;

    /**
     * Factory method to create a Logger instance.
     *
     * @param packageName - Name of the package/service for context
     * @param filename - Source filename for context
     * @returns Logger instance configured with the given context
     *
     * @example
     * const logger = Logger.create('my-service', 'handler.ts');
     */
    static create(packageName: string, filename: string): Logger;

    /**
     * Log debug-level message with optional data.
     */
    debug(message: string, data?: Record<string, any>): void;

    /**
     * Log info-level message with optional data.
     */
    info(message: string, data?: Record<string, any>): void;

    /**
     * Log warning-level message with optional data.
     */
    warn(message: string, data?: Record<string, any>): void;

    /**
     * Log error-level message with optional data.
     */
    error(message: string, data?: Record<string, any>): void;
}
```

#### Usage

```typescript
// Set log level (optional, defaults to 'debug')
process.env.LOG_LEVEL = 'info';

const logger = Logger.create('my-service', 'main.ts');

// Basic logging
logger.debug('Debug message');  // Suppressed when LOG_LEVEL=info
logger.info('Info message');
logger.warn('Warning message');
logger.error('Error message');

// With additional data (object parameter)
logger.info('Request processed', { requestId: 'abc-123', durationMs: 150 });
logger.error('Connection failed', { host: 'localhost', port: 5432, error: 'timeout' });
```

#### Output Format

```json
{
    "timestamp": "2025-01-02T12:00:00.000Z",
    "level": "INFO",
    "context": "my-service:main.ts",
    "message": "Request processed",
    "data": {"requestId": "abc-123", "durationMs": 150}
}
```

---

### ContextBuilder

```typescript
import { ContextBuilder, ContextOptions, ContextExtender } from 'app-yaml-overwrites';
import { FastifyRequest } from 'fastify';

interface ContextOptions {
    env?: Record<string, string>;
    config?: any;
    app?: any;
    state?: any;
    request?: FastifyRequest;
}

/**
 * Context extender function type.
 * Receives current context and optional request, returns additional context.
 */
type ContextExtender = (
    currentContext: any,
    request?: FastifyRequest
) => Promise<any> | any;

class ContextBuilder {
    /**
     * Build resolution context.
     *
     * @param options - Context options
     * @param extenders - Array of extender functions (optional)
     * @returns Promise resolving to combined context object
     *
     * @example
     * const context = await ContextBuilder.build(
     *     { config: rawConfig, app: appInfo },
     *     [authExtender, tenantExtender]
     * );
     */
    static async build(
        options: ContextOptions,
        extenders?: ContextExtender[]
    ): Promise<any>;
}
```

#### Usage

```typescript
// Define context extenders
const authExtender: ContextExtender = async (ctx, request) => {
    const authHeader = request?.headers?.authorization as string | undefined;
    return {
        auth: {
            token: authHeader?.replace('Bearer ', '') || null,
            authenticated: !!authHeader
        }
    };
};

const tenantExtender: ContextExtender = async (ctx, request) => {
    const tenantId = (request?.headers?.['x-tenant-id'] as string) || 'default';
    return {
        tenant: {
            id: tenantId,
            name: `Tenant ${tenantId}`,
            // Can access auth from previous extender
            owner: ctx.auth?.userId
        }
    };
};

// Build context
const context = await ContextBuilder.build(
    {
        env: process.env as Record<string, string>,
        config: rawConfig,
        app: { name: 'MyApp', version: '1.0.0' },
        state: { requestCount: 42 },
        request: fastifyRequest
    },
    [authExtender, tenantExtender]
);

// Access context values
console.log(context.env.HOME);
console.log(context.app.name);
console.log(context.auth.token);
console.log(context.tenant.id);
```

---

### OverwriteMerger

```typescript
import { applyOverwrites } from 'app-yaml-overwrites';

/**
 * Deep merge overwriteSection into originalConfig.
 *
 * @param originalConfig - Base configuration object
 * @param overwriteSection - Overwrites to apply
 * @returns New object with overwrites applied
 *
 * Uses lodash.merge for deep merging:
 * - Objects are recursively merged
 * - Arrays are merged by index
 * - Primitives are overwritten
 */
function applyOverwrites(
    originalConfig: any,
    overwriteSection: any
): any;
```

#### Usage

```typescript
// Basic merge
const original = {
    database: {
        host: 'localhost',
        port: 5432,
        password: null  // placeholder
    }
};

const overwrites = {
    database: {
        password: 'secret123'
    }
};

const result = applyOverwrites(original, overwrites);
// result.database.password === 'secret123'
// result.database.host === 'localhost' (preserved)

// overwrite_from_context pattern
const providerConfig = {
    baseUrl: 'https://api.example.com',
    headers: {
        'Authorization': null,
        'X-Tenant-Id': null
    },
    overwrite_from_context: {
        headers: {
            'Authorization': 'Bearer resolved-token',
            'X-Tenant-Id': 'tenant-123'
        }
    }
};

const resolved = applyOverwrites(
    providerConfig,
    providerConfig.overwrite_from_context
);
```

---

### ConfigSDK

```typescript
import { ConfigSDK, ConfigSDKOptions } from 'app-yaml-overwrites';
import { FastifyRequest } from 'fastify';

interface ConfigSDKOptions {
    configDir?: string;
    configPath?: string;
    contextExtenders?: ContextExtender[];
    validateSchema?: boolean;
}

class ConfigSDK {
    private static instance: ConfigSDK;

    /**
     * Async singleton initialization.
     *
     * @param options - SDK configuration options
     * @returns Promise resolving to initialized ConfigSDK instance
     */
    static async initialize(options?: ConfigSDKOptions): Promise<ConfigSDK>;

    /**
     * Get existing SDK instance.
     *
     * @returns Existing ConfigSDK instance
     * @throws Error if initialize() hasn't been called
     */
    static getInstance(): ConfigSDK;

    /**
     * Get raw configuration without resolution.
     */
    getRaw(): any;

    /**
     * Get resolved configuration for given scope.
     *
     * @param scope - Resolution scope (STARTUP or REQUEST)
     * @param request - Fastify request for request-scoped resolution
     * @returns Promise resolving to resolved configuration
     */
    async getResolved(scope: ComputeScope, request?: FastifyRequest): Promise<any>;

    /**
     * Export configuration as JSON.
     *
     * @param options - Export options
     */
    async toJSON(options?: { maskSecrets?: boolean }): Promise<any>;
}
```

#### Usage

```typescript
// Initialize (typically during app startup)
const sdk = await ConfigSDK.initialize({
    contextExtenders: [authExtender, tenantExtender]
});

// Get raw config
const config = sdk.getRaw();
console.log(config.app.name);

// Get resolved config (with template processing)
const resolved = await sdk.getResolved('REQUEST', request);

// Later: access existing instance
const instance = ConfigSDK.getInstance();
```

---

## Fastify Integration

### Plugin Pattern

```typescript
import fp from 'fastify-plugin';
import { FastifyInstance } from 'fastify';
import { ConfigSDK, Logger, ContextBuilder, applyOverwrites } from 'app-yaml-overwrites';

// Type augmentation
declare module 'fastify' {
    interface FastifyInstance {
        config: any;
        configSDK: ConfigSDK;
        logger: Logger;
    }
}

export const configPlugin = fp(async (fastify: FastifyInstance, opts) => {
    const logger = Logger.create('fastify-server', 'config-plugin.ts');

    const sdk = await ConfigSDK.initialize({
        contextExtenders: opts.contextExtenders || []
    });

    const config = sdk.getRaw();
    logger.info('Configuration loaded', { keys: Object.keys(config) });

    fastify.decorate('config', config);
    fastify.decorate('configSDK', sdk);
    fastify.decorate('logger', logger);
});
```

### Server Usage

```typescript
import Fastify from 'fastify';
import { configPlugin } from './plugins/config';

const server = Fastify({ logger: false });

server.register(configPlugin, {
    contextExtenders: [authExtender, tenantExtender]
});

server.get('/health', async (request, reply) => {
    return {
        status: 'healthy',
        app: server.config.app?.name,
        version: server.config.app?.version
    };
});

server.get('/providers/:name', async (request, reply) => {
    const { name } = request.params as { name: string };
    const provider = server.config.providers?.[name];

    const context = await ContextBuilder.build({
        config: server.config,
        request
    }, server.contextExtenders);

    const resolved = applyOverwrites(
        provider,
        resolveTemplates(provider.overwrite_from_context, context)
    );

    return { name, ...resolved };
});

await server.listen({ port: 3000 });
```

---

## Types

### ComputeScope

```typescript
enum ComputeScope {
    STARTUP = 'STARTUP',
    REQUEST = 'REQUEST'
}
```

### Log Levels

Supported log levels (in order of verbosity):
- `trace` - Most verbose
- `debug` - Development debugging
- `info` - General information
- `warn` - Warning messages
- `error` - Error messages only

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `debug` | Logging level: `trace`, `debug`, `info`, `warn`, `error` |

---

## See Also

- [SDK Guide](../../docs/SDK_GUIDE.md)
- [Server Integration](../../docs/SERVER_INTEGRATION.md)
- [Examples](../examples/)
