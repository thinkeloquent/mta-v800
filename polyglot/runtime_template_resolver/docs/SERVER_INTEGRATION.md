# Server Integration Guide for Runtime Template Resolver

This guide covers integrating the Runtime Template Resolver with web frameworks in both Node.js (Fastify) and Python (FastAPI).

## Overview

Both integrations provide:
- Framework-native integration patterns
- Request-scoped template resolution
- Configuration resolution at startup
- Type-safe APIs

## Fastify Integration (Node.js)

The Fastify integration uses a plugin pattern that decorates the request object.

### Pattern: Fastify Plugin

```typescript
import Fastify from 'fastify';
import fastifyTemplateResolver from '@internal/runtime-template-resolver/integrations/fastify-plugin';
import { MissingStrategy } from '@internal/runtime-template-resolver';

const server = Fastify({ logger: true });

// Register plugin
await server.register(fastifyTemplateResolver, {
    missingStrategy: MissingStrategy.EMPTY
});

// Use in route handlers
server.get('/greet', async (request, reply) => {
    const name = (request.query as any).name || 'World';
    const result = request.resolveTemplate(
        'Hello, {{name}}!',
        { name }
    );
    return { message: result };
});

await server.listen({ port: 3000 });
```

### Usage

The plugin adds `resolveTemplate` to the request object:

```typescript
server.get('/example', async (request) => {
    // Simple resolution
    const greeting = request.resolveTemplate(
        'Hello {{user.name}}!',
        { user: { name: 'Alice' } }
    );

    // With custom options
    const config = request.resolveTemplate(
        '{{host | "localhost"}}:{{port | "3000"}}',
        {},
        { missingStrategy: MissingStrategy.DEFAULT }
    );

    return { greeting, config };
});
```

### Configuration at Startup

```typescript
import { TemplateResolver } from '@internal/runtime-template-resolver';

const APP_CONFIG = {
    database: { url: 'postgres://{{db.host}}/{{db.name}}' }
};

const resolver = new TemplateResolver();
const resolvedConfig = resolver.resolveObject(APP_CONFIG, {
    db: { host: 'localhost', name: 'mydb' }
});

// Decorate server
server.decorate('config', resolvedConfig);

server.addHook('onReady', () => {
    console.log('Database URL:', server.config.database.url);
});
```

## FastAPI Integration (Python)

The FastAPI integration uses dependency injection with a protocol-based resolver.

### Pattern: Dependency Injection

```python
from fastapi import FastAPI, Depends
from typing import Annotated

from runtime_template_resolver import ResolverOptions, MissingStrategy
from runtime_template_resolver.integrations.fastapi_utils import (
    create_resolver_dependency,
    ConfiguredResolverProtocol,
)

app = FastAPI()

# Create dependency
get_resolver = create_resolver_dependency(
    options=ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
)

# Use in route handlers
@app.get("/greet")
def greet(
    name: str = "World",
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)] = None
):
    result = resolver.resolve("Hello, {{name}}!", {"name": name})
    return {"message": result}
```

### Usage

The dependency provides a resolver instance with `resolve` and `resolve_object` methods:

```python
@app.get("/example")
def example(
    resolver: Annotated[ConfiguredResolverProtocol, Depends(get_resolver)]
):
    # Simple resolution
    greeting = resolver.resolve(
        "Hello {{user.name}}!",
        {"user": {"name": "Alice"}}
    )

    # Object resolution
    config = {"url": "https://{{host}}/api"}
    resolved = resolver.resolve_object(config, {"host": "example.com"})

    return {"greeting": greeting, "config": resolved}
```

### Configuration at Startup

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from runtime_template_resolver import TemplateResolver

APP_CONFIG = {
    "database": {"url": "postgres://{{db.host}}/{{db.name}}"}
}

resolver = TemplateResolver()
resolved_config = resolver.resolve_object(APP_CONFIG, {
    "db": {"host": "localhost", "name": "mydb"}
})

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Database URL: {resolved_config['database']['url']}")
    yield

app = FastAPI(lifespan=lifespan)
```

## Side-by-Side Comparison

### Plugin/Dependency Registration

**Fastify**
```typescript
await server.register(fastifyTemplateResolver, {
    missingStrategy: MissingStrategy.EMPTY
});
```

**FastAPI**
```python
get_resolver = create_resolver_dependency(
    options=ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
)
```

### Route Handler Usage

**Fastify**
```typescript
server.get('/api', async (request) => {
    return request.resolveTemplate('{{name}}', { name: 'World' });
});
```

**FastAPI**
```python
@app.get("/api")
def endpoint(resolver = Depends(get_resolver)):
    return resolver.resolve("{{name}}", {"name": "World"})
```

### Request Context Injection

**Fastify**
```typescript
server.addHook('onRequest', async (request) => {
    (request as any).ctx = {
        user: { name: 'Demo' },
        ip: request.ip
    };
});

server.get('/info', async (request) => {
    const ctx = (request as any).ctx;
    return request.resolveTemplate('{{user.name}} from {{ip}}', ctx);
});
```

**FastAPI**
```python
def get_context(request: Request):
    return {
        "user": {"name": "Demo"},
        "ip": request.client.host
    }

@app.get("/info")
def info(
    resolver = Depends(get_resolver),
    ctx = Depends(get_context)
):
    return resolver.resolve("{{user.name}} from {{ip}}", ctx)
```

## Common Patterns

### Email Templating

**Fastify**
```typescript
const TEMPLATES = {
    welcome: 'Welcome {{name}} to {{app}}!'
};

server.post('/email', async (request) => {
    const { template, context } = request.body;
    return request.resolveTemplate(TEMPLATES[template], context);
});
```

**FastAPI**
```python
TEMPLATES = {
    "welcome": "Welcome {{name}} to {{app}}!"
}

@app.post("/email")
def send_email(template: str, context: dict, resolver = Depends(get_resolver)):
    return resolver.resolve(TEMPLATES[template], context)
```

### Health Endpoints with Config

**Fastify**
```typescript
server.get('/health', async () => ({
    status: 'ok',
    database: server.config.database.url
}));
```

**FastAPI**
```python
@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": resolved_config["database"]["url"]
    }
```

## Testing

### Fastify

```typescript
import { test } from 'node:test';
import Fastify from 'fastify';
import fastifyTemplateResolver from './plugin';

test('resolves template', async () => {
    const server = Fastify();
    await server.register(fastifyTemplateResolver);

    server.get('/test', async (request) => {
        return request.resolveTemplate('{{name}}', { name: 'Test' });
    });

    const response = await server.inject({
        method: 'GET',
        url: '/test'
    });

    assert.equal(response.body, 'Test');
});
```

### FastAPI

```python
from fastapi.testclient import TestClient

def test_resolves_template():
    client = TestClient(app)
    response = client.get("/greet?name=Test")
    assert response.json()["message"] == "Hello, Test!"
```

## Best Practices

1. **Register early**: Register the plugin/dependency before defining routes
2. **Use startup resolution**: Resolve configuration templates at application startup
3. **Type your decorators**: Use TypeScript module augmentation or Python protocols
4. **Handle errors gracefully**: Don't expose template errors to end users
5. **Test integrations**: Write integration tests for your template-using endpoints
