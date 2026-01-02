# app_yaml_overwrites SDK Guide

The `app_yaml_overwrites` SDK provides a high-level API for CLI tools, LLM Agents, and Developer Tools to interact with the unified configuration system. It combines static YAML configuration loading with runtime template resolution and context-aware overwrites.

## Overview

The SDK provides:
- **Logger**: Standardized JSON logging with level control
- **ContextBuilder**: Build resolution context with custom extenders
- **OverwriteMerger**: Deep merge configurations with overwrites
- **ConfigSDK**: Unified interface wrapping all components

## Usage

### Node.js

```typescript
import { ConfigSDK, Logger, ContextBuilder, applyOverwrites } from 'app-yaml-overwrites';

// =============================================================================
// Logger Usage
// =============================================================================

const logger = Logger.create('my-service', 'handler.ts');

logger.debug('Processing request', { requestId: 'abc-123' });
logger.info('Request completed', { duration: 150 });
logger.warn('Rate limit approaching', { current: 90, limit: 100 });
logger.error('Request failed', { error: 'Connection timeout' });

// =============================================================================
// Context Builder Usage
// =============================================================================

// Define custom extenders
const authExtender = async (ctx, request) => ({
    auth: {
        userId: request?.headers?.['x-user-id'] || 'anonymous',
        roles: ['user']
    }
});

const tenantExtender = async (ctx, request) => ({
    tenant: {
        id: request?.headers?.['x-tenant-id'] || 'default',
        name: 'Default Tenant'
    }
});

// Build context with extenders
const context = await ContextBuilder.build(
    {
        env: process.env,
        config: { app: { name: 'MyApp' } },
        app: { name: 'MyApp', version: '1.0.0' },
        state: { requestCount: 42 },
        request: fastifyRequest  // optional
    },
    [authExtender, tenantExtender]
);

console.log(context.auth.userId);    // 'user-123'
console.log(context.tenant.id);      // 'tenant-456'

// =============================================================================
// Overwrite Merger Usage
// =============================================================================

const providerConfig = {
    baseUrl: 'https://api.example.com',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': null  // placeholder
    },
    overwrite_from_context: {
        headers: {
            'Authorization': 'Bearer resolved-token'
        }
    }
};

const resolved = applyOverwrites(
    providerConfig,
    providerConfig.overwrite_from_context
);

console.log(resolved.headers.Authorization);  // 'Bearer resolved-token'

// =============================================================================
// ConfigSDK Usage (Full Integration)
// =============================================================================

// Initialize SDK (singleton)
const sdk = await ConfigSDK.initialize({
    contextExtenders: [authExtender, tenantExtender]
});

// Get raw configuration
const raw = sdk.getRaw();

// Get resolved configuration (with template processing)
const resolved = await sdk.getResolved('REQUEST', request);

// Export as JSON
const json = await sdk.toJSON();
```

### Python

```python
from app_yaml_overwrites import ConfigSDK
from app_yaml_overwrites.logger import Logger
from app_yaml_overwrites.context_builder import ContextBuilder
from app_yaml_overwrites.overwrite_merger import apply_overwrites

# =============================================================================
# Logger Usage
# =============================================================================

logger = Logger.create('my-service', 'handler.py')

logger.debug('Processing request', request_id='abc-123')
logger.info('Request completed', duration=150)
logger.warn('Rate limit approaching', current=90, limit=100)
logger.error('Request failed', error='Connection timeout')

# =============================================================================
# Context Builder Usage
# =============================================================================

# Define custom extenders
async def auth_extender(ctx, request):
    return {
        'auth': {
            'user_id': getattr(request, 'headers', {}).get('x-user-id', 'anonymous'),
            'roles': ['user']
        }
    }

async def tenant_extender(ctx, request):
    return {
        'tenant': {
            'id': getattr(request, 'headers', {}).get('x-tenant-id', 'default'),
            'name': 'Default Tenant'
        }
    }

# Build context with extenders
context = await ContextBuilder.build(
    {
        'env': dict(os.environ),
        'config': {'app': {'name': 'MyApp'}},
        'app': {'name': 'MyApp', 'version': '1.0.0'},
        'state': {'request_count': 42},
        'request': fastapi_request  # optional
    },
    extenders=[auth_extender, tenant_extender]
)

print(context['auth']['user_id'])    # 'user-123'
print(context['tenant']['id'])       # 'tenant-456'

# =============================================================================
# Overwrite Merger Usage
# =============================================================================

provider_config = {
    'base_url': 'https://api.example.com',
    'headers': {
        'Content-Type': 'application/json',
        'Authorization': None  # placeholder
    },
    'overwrite_from_context': {
        'headers': {
            'Authorization': 'Bearer resolved-token'
        }
    }
}

resolved = apply_overwrites(
    provider_config,
    provider_config.get('overwrite_from_context', {})
)

print(resolved['headers']['Authorization'])  # 'Bearer resolved-token'

# =============================================================================
# ConfigSDK Usage (Full Integration)
# =============================================================================

# Initialize SDK (singleton)
sdk = await ConfigSDK.initialize({
    'context_extenders': [auth_extender, tenant_extender]
})

# Get raw configuration
raw = sdk.get_raw()

# Get resolved configuration (with template processing)
resolved = await sdk.get_resolved('REQUEST', request)

# Export as JSON
json_data = await sdk.to_json()
```

## Features

### Logger Operations
- `create(packageName, filename)`: Factory method to create logger instance
- `debug(message, data?)`: Log debug-level message
- `info(message, data?)`: Log info-level message
- `warn(message, data?)`: Log warning-level message
- `error(message, data?)`: Log error-level message

### Context Builder Operations
- `build(options, extenders?)`: Build resolution context with optional extenders

### Overwrite Merger Operations
- `applyOverwrites(original, overwrites)`: Deep merge overwrites into original

### ConfigSDK Operations
- `initialize(options)`: Async singleton initialization
- `getInstance()`: Get existing SDK instance
- `getRaw()`: Get raw configuration
- `getResolved(scope, request?)`: Get resolved configuration
- `toJSON(options?)`: Export configuration as JSON

## Configuration Patterns

### overwrite_from_context Pattern

The `overwrite_from_context` pattern allows runtime values to be merged into static configuration:

```yaml
providers:
  payment_api:
    base_url: https://api.example.com
    headers:
      Content-Type: application/json
      Authorization: null  # placeholder
      X-Tenant-Id: null    # placeholder
    overwrite_from_context:
      headers:
        Authorization: "Bearer {{auth.token}}"
        X-Tenant-Id: "{{tenant.id}}"
```

At resolution time:
1. Templates like `{{auth.token}}` are resolved from context
2. The `overwrite_from_context` section is merged into the parent
3. Placeholders (`null`) are replaced with resolved values

### Context Extender Pattern

Extenders add custom context during resolution:

```typescript
// Auth extender - runs first
const authExtender = async (ctx, req) => ({
    auth: { token: req?.headers?.authorization }
});

// Tenant extender - can access auth from previous extender
const tenantExtender = async (ctx, req) => ({
    tenant: {
        id: req?.headers?.['x-tenant-id'],
        owner: ctx.auth?.userId  // from previous extender
    }
});
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `debug` | Logging verbosity: `trace`, `debug`, `info`, `warn`, `error` |

## See Also

- [API Reference](./API_REFERENCE.md) - Complete type signatures
- [Server Integration](./SERVER_INTEGRATION.md) - Fastify and FastAPI patterns
- [Behavioral Differences](./BEHAVIORAL_DIFFERENCES.md) - Language-specific details
