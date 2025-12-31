# Runtime Template Resolver SDK Guide

The Runtime Template Resolver SDK provides a high-level API for resolving template strings with dynamic placeholders. It's designed for CLI tools, LLM Agents, and configuration management systems.

## Overview

The SDK enables:
- **Simple placeholder resolution**: `{{name}}` → `"Alice"`
- **Nested path access**: `{{user.profile.name}}` → `"Alice"`
- **Array indexing**: `{{items[0]}}` → `"apple"`
- **Default values**: `{{port | "3000"}}` → `"3000"`
- **Configuration resolution**: Resolve entire config objects

## Usage

### Node.js

```typescript
import { SDK } from '@internal/runtime-template-resolver';

// Initialize and use directly (no builder needed)
const result = SDK.resolve('Hello {{name}}!', { name: 'World' });
console.log(result);  // Hello World!

// Resolve configuration objects
const config = {
    database: {
        url: 'postgres://{{db.host}}:{{db.port}}/{{db.name}}'
    }
};
const resolved = SDK.resolveObject(config, {
    db: { host: 'localhost', port: '5432', name: 'myapp' }
});
console.log(resolved.database.url);  // postgres://localhost:5432/myapp

// Compile for repeated use
const template = SDK.compile('Order #{{id}} - {{status}}');
for (const order of orders) {
    console.log(template({ id: order.id, status: order.status }));
}
```

### Python

```python
from runtime_template_resolver import resolve, resolve_object, compile

# Resolve single template
result = resolve("Hello {{name}}!", {"name": "World"})
print(result)  # Hello World!

# Resolve configuration objects
config = {
    "database": {
        "url": "postgres://{{db.host}}:{{db.port}}/{{db.name}}"
    }
}
resolved = resolve_object(config, {
    "db": {"host": "localhost", "port": "5432", "name": "myapp"}
})
print(resolved["database"]["url"])  # postgres://localhost:5432/myapp

# Compile for repeated use
template = compile("Order #{{id}} - {{status}}")
for order in orders:
    print(template({"id": order.id, "status": order.status}))
```

## Features

### Core Operations

| Operation | Node.js | Python | Description |
|-----------|---------|--------|-------------|
| Resolve single | `SDK.resolve()` | `resolve()` | Resolve one template |
| Resolve many | `SDK.resolveMany()` | `resolve_many()` | Resolve multiple templates |
| Resolve object | `SDK.resolveObject()` | `resolve_object()` | Resolve templates in objects |

### Validation Operations

| Operation | Node.js | Python | Description |
|-----------|---------|--------|-------------|
| Validate template | `SDK.validate()` | `validate()` | Check template syntax |
| Validate placeholder | `validatePlaceholder()` | `validate_placeholder()` | Check single key |

### Utility Operations

| Operation | Node.js | Python | Description |
|-----------|---------|--------|-------------|
| Extract keys | `SDK.extract()` | `extract()` | Get placeholder keys |
| Compile | `SDK.compile()` | `compile()` | Pre-compile template |

## Template Syntax

### Basic Placeholders

```
{{name}}           → Simple key
{{user.name}}      → Nested path
{{items[0]}}       → Array index
{{data["key"]}}    → Bracket notation
```

### Default Values

```
{{host | "localhost"}}   → Double quotes
{{port | '3000'}}        → Single quotes
{{env | production}}     → No quotes
```

### Whitespace

Whitespace inside placeholders is trimmed:
```
{{  name  }}  →  same as {{name}}
```

## Missing Value Strategies

Control how missing placeholders are handled:

### Node.js

```typescript
import { SDK, MissingStrategy } from '@internal/runtime-template-resolver';

// EMPTY (default) - Replace with empty string
SDK.resolve('{{missing}}', {}, { missingStrategy: MissingStrategy.EMPTY });
// Returns: ""

// KEEP - Keep original placeholder
SDK.resolve('{{missing}}', {}, { missingStrategy: MissingStrategy.KEEP });
// Returns: "{{missing}}"

// ERROR - Throw exception
SDK.resolve('{{missing}}', {}, {
    missingStrategy: MissingStrategy.ERROR,
    throwOnError: true
});
// Throws: MissingValueError
```

### Python

```python
from runtime_template_resolver import resolve, ResolverOptions, MissingStrategy

# EMPTY (default) - Replace with empty string
resolve("{{missing}}", {}, options=ResolverOptions(missing_strategy=MissingStrategy.EMPTY))
# Returns: ""

# KEEP - Keep original placeholder
resolve("{{missing}}", {}, options=ResolverOptions(missing_strategy=MissingStrategy.KEEP))
# Returns: "{{missing}}"

# ERROR - Raise exception
resolve("{{missing}}", {}, options=ResolverOptions(
    missing_strategy=MissingStrategy.ERROR,
    throw_on_error=True
))
# Raises: MissingValueError
```

## Security Features

The SDK prevents access to private/dangerous attributes:

### Node.js

```typescript
import { SDK, SecurityError } from '@internal/runtime-template-resolver';

try {
    SDK.resolve('{{_private}}', { _private: 'secret' }, { throwOnError: true });
} catch (e) {
    if (e instanceof SecurityError) {
        console.log('Blocked:', e.message);
    }
}
```

### Python

```python
from runtime_template_resolver import resolve, ResolverOptions, SecurityError

try:
    resolve("{{_private}}", {"_private": "secret"},
            options=ResolverOptions(throw_on_error=True))
except SecurityError as e:
    print(f"Blocked: {e}")
```

Protected patterns:
- `_private` - Single underscore prefix
- `__dunder__` - Double underscore (dunder) attributes
- `__proto__` - JavaScript prototype chain

## Error Handling

### Node.js

```typescript
import {
    SDK,
    SecurityError,
    ValidationError,
    MissingValueError
} from '@internal/runtime-template-resolver';

try {
    const result = SDK.resolve(template, context, { throwOnError: true });
} catch (e) {
    if (e instanceof SecurityError) {
        // Private attribute access attempted
    } else if (e instanceof ValidationError) {
        // Invalid template syntax
    } else if (e instanceof MissingValueError) {
        // Missing value with ERROR strategy
    }
}
```

### Python

```python
from runtime_template_resolver import (
    resolve,
    ResolverOptions,
    SecurityError,
    ValidationError,
    MissingValueError,
)

try:
    result = resolve(template, context, options=ResolverOptions(throw_on_error=True))
except SecurityError as e:
    # Private attribute access attempted
    pass
except ValidationError as e:
    # Invalid template syntax
    pass
except MissingValueError as e:
    # Missing value with ERROR strategy
    pass
```

## Best Practices

1. **Compile templates for reuse**: If using the same template multiple times, compile it once
2. **Use default values**: Provide sensible defaults for optional placeholders
3. **Validate early**: Validate templates at startup to catch errors early
4. **Choose appropriate missing strategy**: Use KEEP for debugging, EMPTY for production
5. **Don't expose errors to users**: Handle errors gracefully in production
