# Server Integration Guide for app_yaml_overwrites

This document describes integration patterns for using `app_yaml_overwrites` with Fastify (Node.js) and FastAPI (Python) web frameworks.

## Overview

Server integration enables:
- Configuration loading during server startup
- Request-scoped context resolution
- Dependency injection for configuration access
- Health check endpoints with config info

---

## Fastify Integration (Node.js)

The integration uses Fastify's plugin system to load configuration during startup and provide access throughout the application lifecycle.

### Pattern: Fastify Plugin

```typescript
// plugins/config.ts
import fp from 'fastify-plugin';
import { ConfigSDK, Logger, ContextBuilder, applyOverwrites } from 'app-yaml-overwrites';
import { FastifyInstance, FastifyRequest } from 'fastify';

// Type augmentation for Fastify instance
declare module 'fastify' {
    interface FastifyInstance {
        config: ReturnType<ConfigSDK['getRaw']>;
        configSDK: ConfigSDK;
        logger: Logger;
    }
}

export const configPlugin = fp(async (fastify: FastifyInstance, opts) => {
    const logger = Logger.create('fastify-server', 'config-plugin.ts');

    // Initialize SDK during plugin registration
    const sdk = await ConfigSDK.initialize({
        contextExtenders: opts.contextExtenders || []
    });

    const config = sdk.getRaw();
    logger.info('Configuration loaded', { keys: Object.keys(config) });

    // Decorate fastify instance
    fastify.decorate('config', config);
    fastify.decorate('configSDK', sdk);
    fastify.decorate('logger', logger);
});
```

### Usage

```typescript
// server.ts
import Fastify from 'fastify';
import { configPlugin } from './plugins/config';

const server = Fastify({ logger: false });

// Context extenders
const authExtender = async (ctx, req) => ({
    auth: {
        token: req?.headers?.authorization?.replace('Bearer ', '') || null,
        authenticated: !!req?.headers?.authorization
    }
});

const tenantExtender = async (ctx, req) => ({
    tenant: {
        id: req?.headers?.['x-tenant-id'] || 'default'
    }
});

// Register plugin with extenders
server.register(configPlugin, {
    contextExtenders: [authExtender, tenantExtender]
});

// Health endpoint
server.get('/health', async (request, reply) => {
    return {
        status: 'healthy',
        app: server.config.app?.name,
        version: server.config.app?.version
    };
});

// Provider endpoint with resolution
server.get('/providers/:name', async (request, reply) => {
    const { name } = request.params as { name: string };
    const provider = server.config.providers?.[name];

    if (!provider) {
        return reply.status(404).send({ error: 'Provider not found' });
    }

    // Build context for this request
    const context = await ContextBuilder.build({
        config: server.config,
        app: server.config.app,
        request
    }, [authExtender, tenantExtender]);

    // Resolve templates and apply overwrites
    const resolved = applyOverwrites(
        provider,
        resolveTemplates(provider.overwrite_from_context, context)
    );

    return { name, ...resolved, resolved: true };
});

await server.listen({ port: 3000 });
```

### Lifecycle Hook Pattern

```typescript
// Alternative: Use lifecycle hooks for SDK initialization

server.addHook('onReady', async () => {
    const sdk = await ConfigSDK.initialize();
    server.log.info('ConfigSDK initialized');
});

server.addHook('preHandler', async (request, reply) => {
    // Build request-scoped context
    request.context = await ContextBuilder.build({
        config: server.config,
        request
    }, server.contextExtenders);
});
```

---

## FastAPI Integration (Python)

The integration uses FastAPI's lifespan context manager for startup initialization and dependency injection for request-scoped access.

### Pattern: Lifespan Context Manager

```python
# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, Request

from app_yaml_overwrites import ConfigSDK
from app_yaml_overwrites.logger import Logger
from app_yaml_overwrites.context_builder import ContextBuilder
from app_yaml_overwrites.overwrite_merger import apply_overwrites

# Logger
logger = Logger.create('fastapi-server', 'main.py')

# Application state
class AppState:
    config: dict = {}
    sdk: ConfigSDK = None

app_state = AppState()

# Context extenders
async def auth_extender(ctx, request):
    auth_header = request.headers.get('authorization', '') if request else ''
    return {
        'auth': {
            'token': auth_header.replace('Bearer ', '') if auth_header else None,
            'authenticated': bool(auth_header)
        }
    }

async def tenant_extender(ctx, request):
    tenant_id = request.headers.get('x-tenant-id', 'default') if request else 'default'
    return {
        'tenant': {
            'id': tenant_id
        }
    }

CONTEXT_EXTENDERS = [auth_extender, tenant_extender]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info('Starting application')

    sdk = await ConfigSDK.initialize({
        'context_extenders': CONTEXT_EXTENDERS
    })

    app_state.sdk = sdk
    app_state.config = sdk.get_raw()

    logger.info('Configuration loaded', keys=list(app_state.config.keys()))

    yield

    # Shutdown
    logger.info('Shutting down application')

app = FastAPI(
    title='app_yaml_overwrites Example',
    lifespan=lifespan
)
```

### Pattern: Dependency Injection

```python
# dependencies.py
from typing import Annotated, Dict, Any
from fastapi import Depends, Request

async def get_config() -> Dict[str, Any]:
    """Dependency: Get raw configuration."""
    return app_state.config

async def get_context(request: Request) -> Dict[str, Any]:
    """Dependency: Build request-scoped context."""
    return await ContextBuilder.build(
        {
            'config': app_state.config,
            'app': app_state.config.get('app', {}),
            'request': request
        },
        extenders=CONTEXT_EXTENDERS
    )

# Type aliases for cleaner route signatures
Config = Annotated[Dict[str, Any], Depends(get_config)]
Context = Annotated[Dict[str, Any], Depends(get_context)]
```

### Usage

```python
# routes.py
from fastapi import HTTPException

@app.get('/health')
async def health_check(config: Config):
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'app': config.get('app', {}).get('name'),
        'version': config.get('app', {}).get('version')
    }

@app.get('/providers/{name}')
async def get_provider(
    name: str,
    config: Config,
    context: Context
):
    """Get resolved provider configuration."""
    providers = config.get('providers', {})

    if name not in providers:
        raise HTTPException(status_code=404, detail='Provider not found')

    provider = providers[name]
    overwrites = provider.get('overwrite_from_context', {})

    # Resolve templates and apply overwrites
    resolved_overwrites = resolve_templates(overwrites, context)
    resolved = apply_overwrites(provider, resolved_overwrites)

    return {'name': name, **resolved, 'resolved': True}

@app.get('/context')
async def get_current_context(context: Context):
    """Debug endpoint: View current resolution context."""
    return {
        'keys': list(context.keys()),
        'auth': context.get('auth', {}),
        'tenant': context.get('tenant', {})
    }
```

### Middleware Pattern (Alternative)

```python
from starlette.middleware.base import BaseHTTPMiddleware

class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Build context before request handler
        request.state.context = await ContextBuilder.build(
            {
                'config': app_state.config,
                'request': request
            },
            extenders=CONTEXT_EXTENDERS
        )
        return await call_next(request)

app.add_middleware(ContextMiddleware)
```

---

## Common Patterns

### Template Resolution Helper

Both frameworks need a template resolution helper:

**TypeScript**
```typescript
function resolveTemplates(obj: any, context: any): any {
    if (typeof obj === 'string' && obj.startsWith('{{') && obj.endsWith('}}')) {
        const path = obj.slice(2, -2).trim();
        return path.split('.').reduce((acc, key) => acc?.[key], context);
    }
    if (Array.isArray(obj)) {
        return obj.map(item => resolveTemplates(item, context));
    }
    if (obj && typeof obj === 'object') {
        return Object.fromEntries(
            Object.entries(obj).map(([k, v]) => [k, resolveTemplates(v, context)])
        );
    }
    return obj;
}
```

**Python**
```python
def resolve_templates(obj, context):
    if isinstance(obj, str) and obj.startswith('{{') and obj.endswith('}}'):
        path = obj[2:-2].strip()
        value = context
        for key in path.split('.'):
            value = value.get(key) if isinstance(value, dict) else None
        return value
    if isinstance(obj, list):
        return [resolve_templates(item, context) for item in obj]
    if isinstance(obj, dict):
        return {k: resolve_templates(v, context) for k, v in obj.items()}
    return obj
```

### Health Check with Config Info

Both frameworks should expose configuration info in health checks:

```json
{
    "status": "healthy",
    "app": "MyApp",
    "version": "1.0.0",
    "providers": ["userApi", "paymentApi"],
    "features": {
        "caching": true
    }
}
```

---

## See Also

- [API Reference](./API_REFERENCE.md) - Complete type signatures
- [SDK Guide](./SDK_GUIDE.md) - High-level usage patterns
- [Behavioral Differences](./BEHAVIORAL_DIFFERENCES.md) - Language-specific details
- [Examples](../examples/) - Working example applications
