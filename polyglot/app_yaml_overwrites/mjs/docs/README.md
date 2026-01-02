# app_yaml_overwrites (Node.js/TypeScript)

Unified Configuration SDK for Node.js applications. Provides standardized logging, context building, and configuration merging for Fastify and other Node.js frameworks.

## Installation

```bash
npm install app-yaml-overwrites
# or
pnpm add app-yaml-overwrites
```

## Quick Start

### Logger

```typescript
import { Logger } from 'app-yaml-overwrites';

const logger = Logger.create('my-service', 'main.ts');

logger.info('Application started', { version: '1.0.0' });
logger.error('Connection failed', { host: 'localhost', error: 'timeout' });
```

### Context Builder

```typescript
import { ContextBuilder, ContextExtender } from 'app-yaml-overwrites';

const authExtender: ContextExtender = async (ctx, request) => ({
    auth: { userId: 'user-123' }
});

const context = await ContextBuilder.build(
    { config, app: appInfo },
    [authExtender]
);
```

### Overwrite Merger

```typescript
import { applyOverwrites } from 'app-yaml-overwrites';

const resolved = applyOverwrites(
    originalConfig,
    config.overwrite_from_context
);
```

### Fastify Integration

```typescript
import Fastify from 'fastify';
import { ConfigSDK, Logger } from 'app-yaml-overwrites';

const server = Fastify();

server.register(async (fastify) => {
    const sdk = await ConfigSDK.initialize();
    fastify.decorate('config', sdk.getRaw());
});

server.get('/health', async () => ({
    status: 'healthy',
    app: server.config.app?.name
}));

await server.listen({ port: 3000 });
```

## Features

- **Logger**: JSON-structured logging with `LOG_LEVEL` control
- **ContextBuilder**: Build resolution context with async extenders
- **applyOverwrites**: Deep merge `overwrite_from_context` sections (uses lodash)
- **ConfigSDK**: High-level singleton for configuration management

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `debug` | Logging level: `trace`, `debug`, `info`, `warn`, `error` |

## Documentation

- [API Reference](./API_REFERENCE.md) - Complete TypeScript API
- [Examples](../examples/) - Working example code
- [Common Docs](../../docs/) - Cross-language documentation

## Development

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

## Project Structure

```
mjs/
├── src/
│   ├── index.ts
│   ├── logger.ts
│   ├── context-builder.ts
│   ├── overwrite-merger.ts
│   ├── sdk.ts
│   └── cli.ts
├── __tests__/
│   ├── helpers/
│   │   └── test-utils.mjs
│   ├── logger.test.mjs
│   ├── context-builder.test.mjs
│   ├── overwrite-merger.test.mjs
│   └── sdk.test.mjs
├── examples/
│   ├── basic-usage.ts
│   └── fastify-app/
├── docs/
│   ├── README.md
│   └── API_REFERENCE.md
├── package.json
├── tsconfig.json
└── vitest.config.ts
```

## Dependencies

- `lodash` - Deep merge implementation
- `commander` - CLI support

## Peer Dependencies

- `fastify` (optional) - For Fastify integration

## License

See repository root for license information.
