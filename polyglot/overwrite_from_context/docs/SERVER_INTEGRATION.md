# Server Integration Guide for Runtime Template Resolver

This guide covers framework-specific integration patterns for Fastify (Node.js) and FastAPI (Python). Both integrations handle STARTUP and REQUEST scope resolution automatically.

## Fastify Integration (Node.js)

The integration uses a Fastify plugin that resolves configuration at startup and provides per-request resolution through hooks and decorators.

### Pattern: Fastify Plugin

```typescript
import Fastify from 'fastify';
import { createRegistry, ComputeScope } from 'runtime-template-resolver';
import { contextResolverPlugin } from 'runtime-template-resolver/integrations/fastify';

// Configuration template
const config = {
    app: {
        name: "{{env.APP_NAME | 'MyApp'}}",
        version: '{{fn:get_version}}'
    },
    database: {
        url: '{{fn:build_connection_string}}'
    }
};

// Create registry and register functions
const registry = createRegistry();

registry.register(
    'get_version',
    () => '1.0.0',
    ComputeScope.STARTUP
);

registry.register(
    'build_connection_string',
    (ctx) => {
        const env = ctx?.env || process.env;
        return `postgresql://${env.DB_HOST}:${env.DB_PORT}/${env.DB_NAME}`;
    },
    ComputeScope.STARTUP
);

// Create Fastify app
const app = Fastify({ logger: true });

// Register plugin
await app.register(contextResolverPlugin, {
    config: config,
    registry: registry,
    instanceProperty: 'config',   // Access via app.config
    requestProperty: 'config'     // Access via request.config
});

// Routes can access resolved config
app.get('/health', async (request, reply) => {
    return {
        status: 'healthy',
        app: app.config.app.name,
        version: app.config.app.version
    };
});

// Request-scope resolution
app.get('/request-id', async (request, reply) => {
    const id = await request.resolveContext('{{fn:get_request_id}}');
    return { requestId: id };
});

await app.listen({ port: 3000 });
```

### Plugin Options

```typescript
interface ContextResolverPluginOptions {
    config: Record<string, any>;      // Raw configuration template
    registry?: ComputeRegistry;       // Compute registry (created if not provided)
    instanceProperty?: string;        // Property name on fastify instance (default: 'config')
    requestProperty?: string;         // Property name on request (default: 'config')
    logger?: Logger;                  // Custom logger
}
```

### Available Decorators

| Decorator | Scope | Description |
|-----------|-------|-------------|
| `app.config` | Instance | STARTUP-resolved configuration |
| `request.config` | Request | REQUEST-resolved configuration |
| `request.resolveContext(pattern)` | Request | Resolve single pattern with request context |

## FastAPI Integration (Python)

The integration uses FastAPI's lifespan context manager for STARTUP resolution and dependency injection for REQUEST resolution.

### Pattern: Lifespan Context Manager

```python
from contextlib import asynccontextmanager
from typing import Annotated, Any, Dict

from fastapi import FastAPI, Depends, Request
from runtime_template_resolver import create_registry, ComputeScope
from runtime_template_resolver.integrations.fastapi import (
    resolve_startup,
    get_request_config
)

# Configuration template
MOCK_CONFIG = {
    "app": {
        "name": "{{env.APP_NAME | 'MyApp'}}",
        "version": "{{fn:get_version}}"
    },
    "database": {
        "url": "{{fn:build_connection_string}}"
    }
}

# Create registry and register functions
registry = create_registry()

registry.register(
    "get_version",
    lambda ctx=None: "1.0.0",
    ComputeScope.STARTUP
)

registry.register(
    "build_connection_string",
    lambda ctx: (
        f"postgresql://{ctx.get('env', {}).get('DB_HOST', 'localhost')}:"
        f"{ctx.get('env', {}).get('DB_PORT', '5432')}/"
        f"{ctx.get('env', {}).get('DB_NAME', 'app')}"
    ),
    ComputeScope.STARTUP
)

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Resolve configuration
    await resolve_startup(
        app,
        config=MOCK_CONFIG,
        registry=registry,
        state_property="config"
    )
    print(f"App started: {app.state.config['app']['name']}")

    yield

    # SHUTDOWN: Cleanup if needed
    print("App shutting down...")

app = FastAPI(lifespan=lifespan)

# Type alias for dependency injection
ResolvedConfig = Annotated[Dict[str, Any], Depends(get_request_config)]

# Routes
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "app": app.state.config["app"]["name"],
        "version": app.state.config["app"]["version"]
    }

@app.get("/config")
async def get_config(config: ResolvedConfig):
    """Request-scope resolved configuration"""
    return {"resolved_at": "request", "config": config}

@app.get("/request-id")
async def get_request_id(request: Request):
    """Resolve single pattern with request context"""
    resolver = request.app.state._context_resolver
    request_id = await resolver.resolve(
        "{{fn:get_request_id}}",
        {"env": dict(os.environ), "request": request},
        scope=ComputeScope.REQUEST
    )
    return {"request_id": request_id}
```

### Integration Functions

| Function | Description |
|----------|-------------|
| `resolve_startup(app, config, registry, state_property)` | Resolve config at STARTUP, store in `app.state` |
| `get_request_config(request)` | Dependency that returns REQUEST-resolved config |

### App State Properties

After `resolve_startup()`:

| Property | Description |
|----------|-------------|
| `app.state.config` | STARTUP-resolved configuration |
| `app.state._context_resolver` | ContextResolver instance |
| `app.state._context_registry` | ComputeRegistry instance |
| `app.state._context_raw_config` | Original unresolved config |

## Configuration Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION START                        │
├─────────────────────────────────────────────────────────────┤
│  1. Create Registry                                          │
│  2. Register STARTUP functions                               │
│  3. Register REQUEST functions                               │
│  4. Resolve configuration (STARTUP scope)                   │
│     - STARTUP functions execute and cache                    │
│     - REQUEST functions are SKIPPED                          │
│  5. Store resolved config in app state                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     REQUEST HANDLING                         │
├─────────────────────────────────────────────────────────────┤
│  1. Resolve configuration (REQUEST scope)                   │
│     - STARTUP functions return cached values                │
│     - REQUEST functions execute fresh                        │
│  2. Store in request context                                 │
│  3. Handle route logic                                       │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

1. **Resolve at startup**: Use `ComputeScope.STARTUP` for database connections, API keys, static configuration
2. **Cache startup config**: Store in `app.config` (Fastify) or `app.state.config` (FastAPI)
3. **Use REQUEST scope sparingly**: Only for truly per-request values (request IDs, user context)
4. **Validate early**: Resolve configuration before accepting requests to fail fast on missing values
5. **Sanitize sensitive data**: Redact passwords in logs and API responses
