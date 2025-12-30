# Server Integration Guide - Node.js (Fastify)

This guide covers integrating App YAML Static Config with Fastify applications.

## Fastify Integration

### Pattern: Fastify Plugin

The recommended approach uses Fastify's plugin system to initialize configuration and decorate the server instance.

```typescript
import fp from 'fastify-plugin';
import { AppYamlConfig, AppYamlConfigSDK } from 'app-yaml-static-config';
import * as path from 'path';

interface ConfigPluginOptions {
    configDir?: string;
}

export const configPlugin = fp<ConfigPluginOptions>(async (fastify, opts) => {
    const configDir = opts.configDir || './config';
    const env = process.env.NODE_ENV || 'development';

    // Initialize configuration
    await AppYamlConfig.initialize({
        files: [
            path.join(configDir, 'base.yaml'),
            path.join(configDir, `${env}.yaml`)
        ],
        configDir,
        appEnv: env
    });

    const config = AppYamlConfig.getInstance();
    const sdk = new AppYamlConfigSDK(config);

    fastify.log.info({ providers: sdk.listProviders() }, 'Configuration loaded');

    // Decorate Fastify instance
    fastify.decorate('config', config);
    fastify.decorate('sdk', sdk);
});
```

### Type Augmentation

Add type definitions for decorated properties:

```typescript
// types.d.ts
import { AppYamlConfig, AppYamlConfigSDK } from 'app-yaml-static-config';

declare module 'fastify' {
    interface FastifyInstance {
        config: AppYamlConfig;
        sdk: AppYamlConfigSDK;
    }
}
```

### Route Handlers

Access configuration through `fastify.config` or `fastify.sdk`:

```typescript
import Fastify from 'fastify';
import { configPlugin } from './plugins/config';

const server = Fastify({ logger: true });

// Register plugin
await server.register(configPlugin, { configDir: './config' });

// Routes
server.get('/health', async (request, reply) => {
    return {
        status: 'ok',
        appName: server.config.getNested(['app', 'name']),
        version: server.config.getNested(['app', 'version'])
    };
});

server.get('/config', async (request, reply) => {
    return server.sdk.getAll();
});

server.get('/config/:key', async (request, reply) => {
    const { key } = request.params as { key: string };
    return {
        key,
        value: server.sdk.get(key)
    };
});

server.get('/providers', async (request, reply) => {
    return { providers: server.sdk.listProviders() };
});

server.get('/services', async (request, reply) => {
    return { services: server.sdk.listServices() };
});

server.get('/storages', async (request, reply) => {
    return { storages: server.sdk.listStorages() };
});

// Start server
await server.listen({ port: 3000 });
```

### Complete Example

```typescript
// src/index.ts
import Fastify from 'fastify';
import fp from 'fastify-plugin';
import { AppYamlConfig, AppYamlConfigSDK } from 'app-yaml-static-config';
import * as path from 'path';

// Plugin
const configPlugin = fp(async (fastify, opts: { configDir?: string }) => {
    const configDir = opts.configDir || './config';

    await AppYamlConfig.initialize({
        files: [path.join(configDir, 'base.yaml')],
        configDir
    });

    const config = AppYamlConfig.getInstance();
    fastify.decorate('config', config);
    fastify.decorate('sdk', new AppYamlConfigSDK(config));
});

// Server setup
async function main() {
    const server = Fastify({ logger: true });

    await server.register(configPlugin, { configDir: './config' });

    server.get('/health', async () => ({
        status: 'ok',
        appName: server.config.getNested(['app', 'name'])
    }));

    server.get('/providers', async () => ({
        providers: server.sdk.listProviders()
    }));

    await server.listen({ port: 3000 });
    console.log('Server running on http://localhost:3000');
}

main().catch(console.error);
```

### Lifecycle Hooks

Use Fastify hooks for startup/shutdown logging:

```typescript
const configPlugin = fp(async (fastify, opts) => {
    // Initialize config...
    await AppYamlConfig.initialize({ ... });
    const config = AppYamlConfig.getInstance();
    const sdk = new AppYamlConfigSDK(config);

    fastify.decorate('config', config);
    fastify.decorate('sdk', sdk);

    // onReady hook
    fastify.addHook('onReady', async () => {
        fastify.log.info({
            providers: sdk.listProviders(),
            services: sdk.listServices()
        }, 'Configuration ready');
    });

    // onClose hook
    fastify.addHook('onClose', async () => {
        fastify.log.info('Server shutting down');
    });
});
```

## Testing

Use Fastify's `inject` method for testing:

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Fastify from 'fastify';
import { AppYamlConfig } from 'app-yaml-static-config';
import * as path from 'path';

function resetSingleton() {
    (AppYamlConfig as any)._instance = null;
}

describe('Fastify Integration', () => {
    let server: ReturnType<typeof Fastify>;

    beforeEach(async () => {
        resetSingleton();
        server = Fastify({ logger: false });

        // Initialize config
        await AppYamlConfig.initialize({
            files: [path.join('./fixtures', 'base.yaml')],
            configDir: './fixtures'
        });

        const config = AppYamlConfig.getInstance();
        server.decorate('config', config);

        server.get('/health', async () => ({
            status: 'ok',
            appName: server.config.getNested(['app', 'name'])
        }));

        await server.ready();
    });

    afterEach(async () => {
        await server.close();
        resetSingleton();
    });

    it('should return health status', async () => {
        const response = await server.inject({
            method: 'GET',
            url: '/health'
        });

        expect(response.statusCode).toBe(200);
        expect(response.json().status).toBe('ok');
    });

    it('should return app name from config', async () => {
        const response = await server.inject({
            method: 'GET',
            url: '/health'
        });

        expect(response.json().appName).toBe('test-app');
    });
});
```

## Best Practices

1. **Use fastify-plugin (fp)**: Ensures proper plugin encapsulation and avoids scope issues
2. **Decorate Server**: Store config/SDK on the Fastify instance for global access
3. **Type Augmentation**: Add TypeScript declarations for decorated properties
4. **Environment Variables**: Load environment-specific configuration files
5. **Logging**: Use Fastify's built-in logger for configuration events
6. **Immutability**: Never attempt to modify configuration at runtime
