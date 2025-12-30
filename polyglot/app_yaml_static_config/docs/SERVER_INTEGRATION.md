# Server Integration Guide for App YAML Static Config

This guide covers integrating the App YAML Static Config package with Fastify (Node.js) and FastAPI (Python) web frameworks.

## Fastify Integration (Node.js)

The integration uses Fastify's plugin system and decorators to make configuration available throughout the application.

### Pattern: Fastify Plugin

```typescript
import fp from 'fastify-plugin';
import { AppYamlConfig, AppYamlConfigSDK } from 'app-yaml-static-config';
import * as path from 'path';

export const configPlugin = fp(async (fastify, opts) => {
    // Initialize configuration
    const configDir = opts.configDir || './config';
    await AppYamlConfig.initialize({
        files: [
            path.join(configDir, 'base.yaml'),
            path.join(configDir, `${process.env.NODE_ENV || 'development'}.yaml`)
        ],
        configDir
    });

    const config = AppYamlConfig.getInstance();
    const sdk = new AppYamlConfigSDK(config);

    fastify.log.info({ providers: sdk.listProviders() }, 'Configuration loaded');

    // Decorate Fastify instance
    fastify.decorate('config', config);
    fastify.decorate('sdk', sdk);
});
```

### Usage

```typescript
import Fastify from 'fastify';
import { configPlugin } from './plugins/config';

const server = Fastify({ logger: true });

// Register plugin
server.register(configPlugin, { configDir: './config' });

// Access configuration in routes
server.get('/health', async (request, reply) => {
    return {
        status: 'ok',
        app_name: server.config.getNested(['app', 'name'])
    };
});

server.get('/providers', async (request, reply) => {
    return {
        providers: server.sdk.listProviders()
    };
});

// Start server
await server.listen({ port: 3000 });
```

### Type Augmentation

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

## FastAPI Integration (Python)

The integration uses FastAPI's lifespan context manager to initialize configuration at startup.

### Pattern: Lifespan Context Manager

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app_yaml_static_config import AppYamlConfig, AppYamlConfigSDK
from app_yaml_static_config.types import InitOptions
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    config_dir = os.getenv('CONFIG_DIR', './config')
    env = os.getenv('APP_ENV', 'development')

    options = InitOptions(
        files=[
            os.path.join(config_dir, 'base.yaml'),
            os.path.join(config_dir, f'{env}.yaml')
        ],
        config_dir=config_dir
    )
    AppYamlConfig.initialize(options)
    config = AppYamlConfig.get_instance()

    app.state.config = config
    app.state.sdk = AppYamlConfigSDK(config)

    print(f"Configuration loaded: {app.state.sdk.list_providers()}")

    yield

    # Shutdown (cleanup if needed)
    pass

app = FastAPI(lifespan=lifespan)
```

### Usage

```python
from fastapi import FastAPI, Request

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health(request: Request):
    return {
        "status": "ok",
        "app_name": request.app.state.config.get_nested("app", "name")
    }

@app.get("/providers")
async def list_providers(request: Request):
    return {
        "providers": request.app.state.sdk.list_providers()
    }

@app.get("/config/{key}")
async def get_config(key: str, request: Request):
    return {
        "key": key,
        "value": request.app.state.sdk.get(key)
    }
```

### Pattern: Dependency Injection

```python
from fastapi import Depends, Request
from app_yaml_static_config import AppYamlConfigSDK

def get_sdk(request: Request) -> AppYamlConfigSDK:
    return request.app.state.sdk

@app.get("/services")
async def list_services(sdk: AppYamlConfigSDK = Depends(get_sdk)):
    return {
        "services": sdk.list_services()
    }
```

## Best Practices

1. **Initialize Early**: Load configuration during application startup, before handling requests
2. **Use Decorators/State**: Store configuration on the app instance for global access
3. **Environment-Specific Files**: Load base configuration plus environment-specific overrides
4. **Immutability**: Configuration is immutable by design; create new instances if changes are needed
5. **Singleton Pattern**: Both implementations use singleton pattern to ensure consistent configuration access
