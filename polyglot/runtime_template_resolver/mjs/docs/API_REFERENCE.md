# Runtime Template Resolver - Node.js API Reference

Complete API reference for the Node.js/TypeScript implementation of the runtime template resolver.

## Core Components

### TemplateResolver

The main class for resolving templates with placeholder substitution.

```typescript
import { TemplateResolver, ResolverOptions } from '@internal/runtime-template-resolver';

class TemplateResolver {
    constructor();

    resolve(
        template: string,
        context: Record<string, unknown>,
        options?: ResolverOptions
    ): string;

    resolveObject(
        obj: unknown,
        context: Record<string, unknown>,
        options?: ResolverOptions
    ): unknown;
}
```

### ResolverOptions

Configuration options for template resolution.

```typescript
import { ResolverOptions, MissingStrategy } from '@internal/runtime-template-resolver';

interface ResolverOptions {
    missingStrategy?: MissingStrategy;
    throwOnError?: boolean;
}
```

### MissingStrategy

Enum defining how to handle missing placeholder values.

```typescript
import { MissingStrategy } from '@internal/runtime-template-resolver';

enum MissingStrategy {
    EMPTY = 'empty',      // Replace with empty string
    KEEP = 'keep',        // Keep original placeholder
    ERROR = 'error',      // Throw MissingValueError
    DEFAULT = 'default',  // Use default value if provided
}
```

## SDK Functions

High-level convenience functions for common operations.

```typescript
import {
    SDK,
    validatePlaceholder,
    extractPlaceholders,
} from '@internal/runtime-template-resolver';
```

### SDK.resolve

Resolve a single template string.

```typescript
SDK.resolve(
    template: string,
    context: Record<string, unknown>,
    options?: ResolverOptions
): string;

// Example
const result = SDK.resolve('Hello {{name}}!', { name: 'World' });
// Returns: "Hello World!"
```

### SDK.resolveMany

Resolve multiple templates with the same context.

```typescript
SDK.resolveMany(
    templates: string[],
    context: Record<string, unknown>,
    options?: ResolverOptions
): string[];

// Example
const results = SDK.resolveMany(
    ['Hello {{name}}', 'Count: {{count}}'],
    { name: 'World', count: 42 }
);
// Returns: ["Hello World", "Count: 42"]
```

### SDK.resolveObject

Recursively resolve templates within nested objects.

```typescript
SDK.resolveObject(
    obj: unknown,
    context: Record<string, unknown>,
    options?: ResolverOptions
): unknown;

// Example
const config = { url: 'https://{{host}}/api' };
const resolved = SDK.resolveObject(config, { host: 'example.com' });
// Returns: { url: "https://example.com/api" }
```

### SDK.validate

Validate a template string for syntax errors.

```typescript
SDK.validate(template: string): void;

// Example
SDK.validate('{{user.name}}');  // OK
SDK.validate('{{foo@bar}}');    // Throws ValidationError
```

### SDK.extract

Extract placeholder keys from a template.

```typescript
SDK.extract(template: string): string[];

// Example
const keys = SDK.extract('{{user.name}} at {{company}}');
// Returns: ["user.name", "company"]
```

### SDK.compile

Pre-compile a template for repeated use.

```typescript
SDK.compile(template: string): (context: Record<string, unknown>) => string;

// Example
const emailTemplate = SDK.compile('Dear {{name}}, ...');
const result1 = emailTemplate({ name: 'Alice' });
const result2 = emailTemplate({ name: 'Bob' });
```

### validatePlaceholder

Validate a single placeholder key.

```typescript
validatePlaceholder(placeholder: string): void;

// Example
validatePlaceholder('user.profile.name');  // OK
validatePlaceholder('_private');           // Throws ValidationError
```

### extractPlaceholders

Extract and trim placeholders from a template.

```typescript
extractPlaceholders(template: string): string[];

// Example
const placeholders = extractPlaceholders('{{  name  }}');
// Returns: ["name"]
```

## Exceptions

### SecurityError

Thrown when accessing private or unsafe attributes.

```typescript
import { SecurityError } from '@internal/runtime-template-resolver';

class SecurityError extends Error {
    name: 'SecurityError';
}
```

### ValidationError

Thrown when template syntax is invalid.

```typescript
import { ValidationError } from '@internal/runtime-template-resolver';

class ValidationError extends Error {
    name: 'ValidationError';
}
```

### MissingValueError

Thrown when a required placeholder value is missing (with ERROR strategy).

```typescript
import { MissingValueError } from '@internal/runtime-template-resolver';

class MissingValueError extends Error {
    name: 'MissingValueError';
}
```

## Fastify Integration

### fastifyTemplateResolver Plugin

Fastify plugin for template resolution.

```typescript
import fastifyTemplateResolver from '@internal/runtime-template-resolver/integrations/fastify-plugin';

// Plugin registration
await fastify.register(fastifyTemplateResolver, {
    missingStrategy: MissingStrategy.EMPTY
});
```

### Request Decorator

The plugin decorates the request with a `resolveTemplate` method.

```typescript
declare module 'fastify' {
    interface FastifyRequest {
        resolveTemplate(
            template: string,
            context: Record<string, unknown>,
            options?: ResolverOptions
        ): string;
    }
}

// Usage in route handler
fastify.get('/greet', async (request, reply) => {
    const result = request.resolveTemplate(
        'Hello {{name}}!',
        { name: 'World' }
    );
    return { message: result };
});
```

## Type Exports

```typescript
export {
    // Core
    TemplateResolver,
    ResolverOptions,
    MissingStrategy,

    // SDK
    SDK,

    // Errors
    SecurityError,
    ValidationError,
    MissingValueError,

    // Utilities
    validatePlaceholder,
    extractPlaceholders,

    // Integration
    fastifyTemplateResolver,
};
```
