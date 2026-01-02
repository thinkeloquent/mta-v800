# Runtime Template Resolver SDK Guide

The Runtime Template Resolver SDK provides a high-level API for resolving template patterns (`{{variable.path}}`) and compute patterns (`{{fn:function_name}}`) at runtime. It supports scoped execution (STARTUP vs REQUEST) for configuration management in web applications.

## Installation

### Node.js

```bash
npm install runtime-template-resolver
```

### Python

```bash
pip install runtime-template-resolver
# or with poetry
poetry add runtime-template-resolver
```

## Usage

### Node.js

```typescript
import { createRegistry, createResolver, ComputeScope } from 'runtime-template-resolver';

// Create registry and resolver
const registry = createRegistry();
const resolver = createResolver(registry);

// Register compute functions
registry.register(
    'get_version',
    () => '1.0.0',
    ComputeScope.STARTUP
);

registry.register(
    'get_request_id',
    (ctx) => `req-${Date.now()}`,
    ComputeScope.REQUEST
);

// Resolve patterns
const context = { env: process.env };

// Single pattern
const version = await resolver.resolve('{{fn:get_version}}', context);
console.log('Version:', version);

// Template with default
const appName = await resolver.resolve("{{env.APP_NAME | 'MyApp'}}", context);
console.log('App Name:', appName);

// Resolve entire configuration object
const config = {
    app: {
        name: "{{env.APP_NAME | 'DefaultApp'}}",
        version: '{{fn:get_version}}',
        debug: "{{env.DEBUG | 'false'}}"
    }
};

const resolved = await resolver.resolveObject(config, context, ComputeScope.STARTUP);
console.log('Resolved Config:', resolved);
```

### Python

```python
from runtime_template_resolver import create_registry, create_resolver, ComputeScope
import os

# Create registry and resolver
registry = create_registry()
resolver = create_resolver(registry)

# Register compute functions
registry.register(
    "get_version",
    lambda ctx=None: "1.0.0",
    ComputeScope.STARTUP
)

registry.register(
    "get_request_id",
    lambda ctx: f"req-{id(ctx)}",
    ComputeScope.REQUEST
)

# Resolve patterns
context = {"env": dict(os.environ)}

# Single pattern
version = await resolver.resolve("{{fn:get_version}}", context)
print(f"Version: {version}")

# Template with default
app_name = await resolver.resolve("{{env.APP_NAME | 'MyApp'}}", context)
print(f"App Name: {app_name}")

# Resolve entire configuration object
config = {
    "app": {
        "name": "{{env.APP_NAME | 'DefaultApp'}}",
        "version": "{{fn:get_version}}",
        "debug": "{{env.DEBUG | 'false'}}"
    }
}

resolved = await resolver.resolve_object(config, context, ComputeScope.STARTUP)
print(f"Resolved Config: {resolved}")
```

## Features

### Core Operations

- **Pattern Resolution**: `resolve()` / `resolve()` - Resolve single template or compute pattern
- **Object Resolution**: `resolveObject()` / `resolve_object()` - Recursively resolve all patterns in nested objects
- **Batch Resolution**: `resolveMany()` / `resolve_many()` - Resolve multiple patterns in parallel

### Compute Registry

- **Function Registration**: `register(name, fn, scope)` - Register compute function
- **Function Removal**: `unregister(name)` - Remove registered function
- **Function Lookup**: `has(name)`, `list()`, `getScope(name)` - Query registered functions
- **Cache Management**: `clear()`, `clearCache()` - Clear registry and/or cache

### Scope Enforcement

- **STARTUP scope**: Functions are cached after first execution
- **REQUEST scope**: Functions execute on every call
- **Scope Violation Detection**: Calling REQUEST functions during STARTUP resolution throws `ScopeViolationError`

### Security

- **Path Validation**: Blocks `__proto__`, `constructor`, `prototype` access
- **Underscore Prefix Blocking**: Prevents access to `_private` properties
- **Path Traversal Prevention**: Blocks `..` in paths

## Pattern Syntax

### Template Patterns

```
{{env.APP_NAME}}                    # Access context.env.APP_NAME
{{config.database.host}}            # Nested access
{{env.MISSING | 'default'}}         # With default value
```

### Compute Patterns

```
{{fn:get_version}}                  # Call registered function
{{fn:build_url}}                    # Function receives context
{{fn:optional | 'fallback'}}        # Default on failure
```

### Type Inference

Default values are automatically parsed:

```
{{missing | 'true'}}    -> true (boolean)
{{missing | 'false'}}   -> false (boolean)
{{missing | '42'}}      -> 42 (number/int)
{{missing | '3.14'}}    -> 3.14 (number/float)
{{missing | 'hello'}}   -> "hello" (string)
```

## Best Practices

1. **Register STARTUP functions for static configuration** - Version numbers, build timestamps, connection strings
2. **Register REQUEST functions for dynamic values** - Request IDs, user context, timestamps
3. **Use defaults for optional configuration** - `{{env.DEBUG | 'false'}}`
4. **Validate configuration at startup** - Resolve with `ComputeScope.STARTUP` before accepting requests
5. **Cache resolved configuration** - Don't re-resolve on every request unless using REQUEST-scope functions
