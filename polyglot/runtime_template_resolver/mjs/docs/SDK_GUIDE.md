# Runtime Template Resolver - Node.js SDK Guide

The Runtime Template Resolver SDK provides a high-level API for resolving template strings with dynamic placeholders. It's designed for CLI tools, LLM Agents, and configuration management systems.

## Installation

```bash
npm install @internal/runtime-template-resolver
```

## Quick Start

```typescript
import { SDK } from '@internal/runtime-template-resolver';

// Simple resolution
const message = SDK.resolve('Hello {{name}}!', { name: 'World' });
console.log(message);  // Hello World!

// Resolve configuration objects
const config = {
    database: {
        url: 'postgres://{{db.host}}:{{db.port}}/{{db.name}}'
    }
};
const context = { db: { host: 'localhost', port: '5432', name: 'myapp' } };
const resolved = SDK.resolveObject(config, context) as typeof config;
console.log(resolved.database.url);  // postgres://localhost:5432/myapp
```

## Usage

### Basic Template Resolution

```typescript
import { TemplateResolver } from '@internal/runtime-template-resolver';

const resolver = new TemplateResolver();

// Simple placeholder
const result = resolver.resolve('Hello {{name}}!', { name: 'Alice' });

// Nested paths
const result2 = resolver.resolve(
    'User: {{user.profile.name}}',
    { user: { profile: { name: 'Alice' } } }
);

// Array access
const result3 = resolver.resolve(
    'First item: {{items[0]}}',
    { items: ['apple', 'banana', 'cherry'] }
);
```

### Default Values

```typescript
import { SDK } from '@internal/runtime-template-resolver';

// Double quotes
const result1 = SDK.resolve('Host: {{host | "localhost"}}', {});
// Returns: "Host: localhost"

// Single quotes
const result2 = SDK.resolve("Port: {{port | '5432'}}", {});
// Returns: "Port: 5432"

// No quotes
const result3 = SDK.resolve('Env: {{env | production}}', {});
// Returns: "Env: production"
```

### Missing Value Strategies

```typescript
import {
    TemplateResolver,
    MissingStrategy,
    MissingValueError,
} from '@internal/runtime-template-resolver';

const resolver = new TemplateResolver();
const template = 'Value: {{missing}}';

// EMPTY - Replace with empty string (default)
const result1 = resolver.resolve(template, {}, {
    missingStrategy: MissingStrategy.EMPTY
});
// Returns: "Value: "

// KEEP - Keep original placeholder
const result2 = resolver.resolve(template, {}, {
    missingStrategy: MissingStrategy.KEEP
});
// Returns: "Value: {{missing}}"

// ERROR - Throw exception
try {
    resolver.resolve(template, {}, {
        missingStrategy: MissingStrategy.ERROR,
        throwOnError: true
    });
} catch (e) {
    if (e instanceof MissingValueError) {
        console.log(`Error: ${e.message}`);
    }
}
```

### Template Compilation

For templates used repeatedly, compile them for better performance:

```typescript
import { SDK } from '@internal/runtime-template-resolver';

// Compile once
const emailTemplate = SDK.compile(`
Dear {{name}},

Your order #{{order_id}} has been {{status}}.

Best regards,
{{company}}
`);

// Use multiple times
for (const order of orders) {
    const email = emailTemplate({
        name: order.customerName,
        order_id: order.id,
        status: order.status,
        company: 'ACME Corp'
    });
    sendEmail(email);
}
```

### Validation

```typescript
import {
    SDK,
    validatePlaceholder,
    ValidationError,
} from '@internal/runtime-template-resolver';

// Validate entire template
try {
    SDK.validate('{{user.name}}');  // OK
    SDK.validate('{{foo@bar}}');    // Throws ValidationError
} catch (e) {
    if (e instanceof ValidationError) {
        console.log(`Invalid template: ${e.message}`);
    }
}

// Validate single placeholder
try {
    validatePlaceholder('user.profile.name');  // OK
    validatePlaceholder('_private');           // Throws ValidationError
} catch (e) {
    if (e instanceof ValidationError) {
        console.log(`Invalid placeholder: ${e.message}`);
    }
}
```

### Extracting Placeholders

```typescript
import { SDK, extractPlaceholders } from '@internal/runtime-template-resolver';

// Extract placeholder keys
const keys = SDK.extract('Hello {{name}}, you have {{count}} messages');
console.log(keys);  // ["name", "count"]

// Extract with whitespace handling
const keys2 = extractPlaceholders('{{  name  }}');
console.log(keys2);  // ["name"]
```

## Features

### Core Operations

- `SDK.resolve(template, context)` - Resolve single template
- `SDK.resolveMany(templates, context)` - Resolve multiple templates
- `SDK.resolveObject(obj, context)` - Resolve templates in nested objects

### Validation Operations

- `SDK.validate(template)` - Validate template syntax
- `validatePlaceholder(placeholder)` - Validate single placeholder

### Utility Operations

- `SDK.extract(template)` - Extract placeholder keys
- `extractPlaceholders(template)` - Extract and trim placeholders
- `SDK.compile(template)` - Pre-compile template for reuse

### Security Features

- Private attribute protection (`_private`, `__proto__`)
- Path traversal prevention
- Input validation

## Error Handling

```typescript
import {
    SDK,
    SecurityError,
    ValidationError,
    MissingValueError,
} from '@internal/runtime-template-resolver';

try {
    const result = SDK.resolve('{{_private}}', { _private: 'secret' }, {
        throwOnError: true
    });
} catch (e) {
    if (e instanceof SecurityError) {
        console.log(`Security violation: ${e.message}`);
    } else if (e instanceof ValidationError) {
        console.log(`Invalid template: ${e.message}`);
    } else if (e instanceof MissingValueError) {
        console.log(`Missing value: ${e.message}`);
    }
}
```

## TypeScript Support

Full TypeScript support with strict typing:

```typescript
import {
    TemplateResolver,
    ResolverOptions,
    MissingStrategy,
} from '@internal/runtime-template-resolver';

interface Config {
    database: {
        url: string;
    };
}

const resolver = new TemplateResolver();

const config: Config = {
    database: {
        url: 'postgres://{{host}}/{{db}}'
    }
};

const resolved = resolver.resolveObject(config, {
    host: 'localhost',
    db: 'mydb'
}) as Config;

console.log(resolved.database.url);  // Type-safe access
```
