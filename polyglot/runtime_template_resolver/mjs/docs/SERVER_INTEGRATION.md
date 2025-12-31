# Server Integration Guide - Node.js (Fastify)

This guide covers integrating the Runtime Template Resolver with Fastify applications.

## Overview

The Fastify integration provides:

- Plugin-based resolver registration
- Request decorator for template resolution
- Type-safe TypeScript support
- Configuration resolution at startup

## Installation

```bash
npm install @internal/runtime-template-resolver fastify
```

## Pattern: Fastify Plugin

The recommended pattern uses the built-in Fastify plugin.

### Basic Setup

```typescript
import Fastify from 'fastify';
import fastifyTemplateResolver from '@internal/runtime-template-resolver/integrations/fastify-plugin';
import { MissingStrategy } from '@internal/runtime-template-resolver';

const server = Fastify({ logger: true });

// Register the plugin
await server.register(fastifyTemplateResolver, {
    missingStrategy: MissingStrategy.EMPTY
});

// Use in route handlers
server.get('/greet', async (request, reply) => {
    const name = (request.query as any).name || 'World';
    const result = request.resolveTemplate(
        'Hello, {{name}}! Welcome to our API.',
        { name }
    );
    return { message: result };
});

await server.listen({ port: 3000 });
```

### With Custom Options

```typescript
import fastifyTemplateResolver from '@internal/runtime-template-resolver/integrations/fastify-plugin';
import { MissingStrategy } from '@internal/runtime-template-resolver';

// Keep missing placeholders
await server.register(fastifyTemplateResolver, {
    missingStrategy: MissingStrategy.KEEP
});

// Or in a separate plugin scope
await server.register(async (instance) => {
    await instance.register(fastifyTemplateResolver, {
        missingStrategy: MissingStrategy.ERROR
    });
    // Routes in this scope use ERROR strategy
});
```

## Pattern: Configuration Resolution at Startup

Resolve configuration templates once during server startup.

```typescript
import Fastify, { FastifyInstance } from 'fastify';
import { TemplateResolver, MissingStrategy } from '@internal/runtime-template-resolver';
import fastifyTemplateResolver from '@internal/runtime-template-resolver/integrations/fastify-plugin';

// Configuration with templates
const APP_CONFIG = {
    database: {
        url: 'postgres://{{db.host}}:{{db.port}}/{{db.name}}'
    },
    api: {
        baseUrl: 'https://{{api.domain}}/v{{api.version}}'
    }
};

// Runtime context from environment
const RUNTIME_CONTEXT = {
    db: { host: 'localhost', port: '5432', name: 'myapp' },
    api: { domain: 'api.example.com', version: '2' }
};

// Augment FastifyInstance type
declare module 'fastify' {
    interface FastifyInstance {
        resolvedConfig: typeof APP_CONFIG;
    }
}

async function buildServer(): Promise<FastifyInstance> {
    const server = Fastify({ logger: true });

    // Resolve config at startup
    const resolver = new TemplateResolver();
    const resolvedConfig = resolver.resolveObject(APP_CONFIG, RUNTIME_CONTEXT) as typeof APP_CONFIG;

    // Decorate server with resolved config
    server.decorate('resolvedConfig', resolvedConfig);

    // Register template resolver plugin
    await server.register(fastifyTemplateResolver);

    // Log on ready
    server.addHook('onReady', async () => {
        server.log.info(`Database URL: ${server.resolvedConfig.database.url}`);
        server.log.info(`API Base URL: ${server.resolvedConfig.api.baseUrl}`);
    });

    server.get('/config', async () => ({
        databaseUrl: server.resolvedConfig.database.url,
        apiBaseUrl: server.resolvedConfig.api.baseUrl
    }));

    return server;
}
```

## Pattern: Request Context Injection

Inject request-specific context into templates.

```typescript
import Fastify from 'fastify';
import fastifyTemplateResolver from '@internal/runtime-template-resolver/integrations/fastify-plugin';

const server = Fastify();
await server.register(fastifyTemplateResolver);

// Add hook to build request context
server.addHook('onRequest', async (request) => {
    (request as any).templateContext = {
        user: {
            id: 'user-123',  // From auth token in real app
            name: 'Demo User'
        },
        request: {
            ip: request.ip,
            path: request.url
        }
    };
});

server.get('/user-info', async (request) => {
    const ctx = (request as any).templateContext;
    const template = 'User {{user.name}} accessing {{request.path}} from {{request.ip}}';
    const result = request.resolveTemplate(template, ctx);
    return { message: result, context: ctx };
});
```

## Pattern: Email Templating

Use template resolution for email generation.

```typescript
import Fastify from 'fastify';
import fastifyTemplateResolver from '@internal/runtime-template-resolver/integrations/fastify-plugin';

const server = Fastify();
await server.register(fastifyTemplateResolver);

const EMAIL_TEMPLATES: Record<string, string> = {
    welcome: 'Welcome to {{app.name}}, {{user.name}}!',
    order_confirmation: 'Your order #{{order.id}} for ${{order.total}} is confirmed.',
    password_reset: 'Click here to reset: {{reset_url}}'
};

interface EmailBody {
    template_name: string;
    recipient: string;
    context: Record<string, unknown>;
}

server.post<{ Body: EmailBody }>('/email/preview', async (request, reply) => {
    const { template_name, recipient, context } = request.body;

    if (!(template_name in EMAIL_TEMPLATES)) {
        reply.code(400);
        return { error: `Unknown template: ${template_name}` };
    }

    const template = EMAIL_TEMPLATES[template_name];
    const body = request.resolveTemplate(template, context);

    return {
        to: recipient,
        subject: `Template: ${template_name}`,
        body
    };
});
```

## Complete Example Application

```typescript
import Fastify, { FastifyInstance } from 'fastify';
import { TemplateResolver, MissingStrategy } from '@internal/runtime-template-resolver';
import fastifyTemplateResolver from '@internal/runtime-template-resolver/integrations/fastify-plugin';

// Configuration
const APP_CONFIG = {
    app: { name: 'My API', version: '1.0.0' },
    database: { url: 'postgres://{{db.host}}/{{db.name}}' }
};

const RUNTIME_CONTEXT = {
    db: { host: 'localhost', name: 'mydb' }
};

// Type augmentation
declare module 'fastify' {
    interface FastifyInstance {
        resolvedConfig: typeof APP_CONFIG;
    }
}

async function buildServer(): Promise<FastifyInstance> {
    const server = Fastify({
        logger: {
            level: 'info',
            transport: {
                target: 'pino-pretty'
            }
        }
    });

    // Resolve config
    const resolver = new TemplateResolver();
    const resolvedConfig = resolver.resolveObject(APP_CONFIG, RUNTIME_CONTEXT) as typeof APP_CONFIG;
    server.decorate('resolvedConfig', resolvedConfig);

    // Register plugin
    await server.register(fastifyTemplateResolver, {
        missingStrategy: MissingStrategy.EMPTY
    });

    // Routes
    server.get('/health', async () => ({
        status: 'ok',
        app: server.resolvedConfig.app.name,
        version: server.resolvedConfig.app.version
    }));

    interface ResolveBody {
        template: string;
        context: Record<string, unknown>;
    }

    server.post<{ Body: ResolveBody }>('/resolve', async (request) => {
        const { template, context } = request.body;
        const result = request.resolveTemplate(template, context);
        return { original: template, resolved: result };
    });

    return server;
}

async function main(): Promise<void> {
    const server = await buildServer();

    server.addHook('onReady', async () => {
        console.log('='.repeat(60));
        console.log('Server starting...');
        console.log(`Database URL: ${server.resolvedConfig.database.url}`);
        console.log('='.repeat(60));
    });

    await server.listen({ port: 3000, host: '0.0.0.0' });
}

main();
```

## Running the Application

```bash
# Development with hot reload
npx tsx watch server.ts

# Production
npx tsx server.ts

# Or compile and run
npx tsc && node dist/server.js
```

## Testing Endpoints

```bash
# Health check
curl http://localhost:3000/health

# Resolve template
curl -X POST http://localhost:3000/resolve \
  -H "Content-Type: application/json" \
  -d '{"template": "Hello {{name}}!", "context": {"name": "World"}}'
```

## Type Declaration for Request Decorator

The plugin adds a `resolveTemplate` method to the request object:

```typescript
// In your app or a .d.ts file
declare module 'fastify' {
    interface FastifyRequest {
        resolveTemplate(
            template: string,
            context: Record<string, unknown>,
            options?: import('@internal/runtime-template-resolver').ResolverOptions
        ): string;
    }
}
```
