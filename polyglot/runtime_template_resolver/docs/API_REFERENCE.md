# Runtime Template Resolver API Reference

Complete API reference for the Runtime Template Resolver package, showing type signatures for both TypeScript and Python.

## Core Components

### TemplateResolver

The main class for resolving templates with placeholder substitution.

**TypeScript**
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

**Python**
```python
from runtime_template_resolver import TemplateResolver, ResolverOptions

class TemplateResolver:
    def __init__(self) -> None: ...

    def resolve(
        self,
        template: str,
        context: Dict[str, Any],
        options: Optional[ResolverOptions] = None
    ) -> str: ...

    def resolve_object(
        self,
        obj: Any,
        context: Dict[str, Any],
        options: Optional[ResolverOptions] = None
    ) -> Any: ...
```

### ResolverOptions

Configuration options for template resolution.

**TypeScript**
```typescript
interface ResolverOptions {
    missingStrategy?: MissingStrategy;
    throwOnError?: boolean;
}
```

**Python**
```python
@dataclass
class ResolverOptions:
    missing_strategy: MissingStrategy = MissingStrategy.EMPTY
    throw_on_error: bool = False
```

### MissingStrategy

Enum defining how to handle missing placeholder values.

**TypeScript**
```typescript
enum MissingStrategy {
    EMPTY = 'empty',      // Replace with empty string
    KEEP = 'keep',        // Keep original placeholder
    ERROR = 'error',      // Throw MissingValueError
    DEFAULT = 'default',  // Use default value if provided
}
```

**Python**
```python
class MissingStrategy(Enum):
    EMPTY = "empty"      # Replace with empty string
    KEEP = "keep"        # Keep original placeholder
    ERROR = "error"      # Raise MissingValueError
    DEFAULT = "default"  # Use default value if provided
```

## SDK

High-level convenience functions for common operations.

**TypeScript**
```typescript
import { SDK } from '@internal/runtime-template-resolver';

// Resolve single template
const result = SDK.resolve('Hello {{name}}!', { name: 'World' });

// Resolve multiple templates
const results = SDK.resolveMany(['{{a}}', '{{b}}'], context);

// Resolve templates in objects
const resolved = SDK.resolveObject(config, context);

// Validate template syntax
SDK.validate('{{user.name}}');

// Extract placeholder keys
const keys = SDK.extract('{{name}} at {{company}}');

// Compile template for reuse
const compiled = SDK.compile('Hello {{name}}!');
const result = compiled({ name: 'World' });
```

**Python**
```python
from runtime_template_resolver import (
    resolve,
    resolve_many,
    resolve_object,
    validate,
    extract,
    compile,
)

# Resolve single template
result = resolve("Hello {{name}}!", {"name": "World"})

# Resolve multiple templates
results = resolve_many(["{{a}}", "{{b}}"], context)

# Resolve templates in objects
resolved = resolve_object(config, context)

# Validate template syntax
validate("{{user.name}}")

# Extract placeholder keys
keys = extract("{{name}} at {{company}}")

# Compile template for reuse
compiled = compile("Hello {{name}}!")
result = compiled({"name": "World"})
```

### SDK Operations

| Operation | Description |
|-----------|-------------|
| `resolve(template, context)` | Resolve a single template string |
| `resolveMany(templates, context)` | Resolve multiple templates with same context |
| `resolveObject(obj, context)` | Recursively resolve templates in nested objects |
| `validate(template)` | Validate template syntax, throws on error |
| `extract(template)` | Extract placeholder keys from template |
| `compile(template)` | Pre-compile template for repeated use |

## Errors

### SecurityError

Raised/thrown when accessing private or unsafe attributes.

**TypeScript**
```typescript
import { SecurityError } from '@internal/runtime-template-resolver';

class SecurityError extends Error {
    name: 'SecurityError';
}
```

**Python**
```python
from runtime_template_resolver import SecurityError

class SecurityError(Exception):
    """Raised when access to private/unsafe attribute is denied."""
    pass
```

### ValidationError

Raised/thrown when template syntax is invalid.

**TypeScript**
```typescript
import { ValidationError } from '@internal/runtime-template-resolver';

class ValidationError extends Error {
    name: 'ValidationError';
}
```

**Python**
```python
from runtime_template_resolver import ValidationError

class ValidationError(Exception):
    """Raised when template or placeholder validation fails."""
    pass
```

### MissingValueError

Raised/thrown when a required placeholder value is missing (with ERROR strategy).

**TypeScript**
```typescript
import { MissingValueError } from '@internal/runtime-template-resolver';

class MissingValueError extends Error {
    name: 'MissingValueError';
}
```

**Python**
```python
from runtime_template_resolver import MissingValueError

class MissingValueError(Exception):
    """Raised when a placeholder value is missing."""
    pass
```

## Utility Functions

### validatePlaceholder / validate_placeholder

Validate a single placeholder key.

**TypeScript**
```typescript
import { validatePlaceholder } from '@internal/runtime-template-resolver';

validatePlaceholder(placeholder: string): void;
```

**Python**
```python
from runtime_template_resolver import validate_placeholder

def validate_placeholder(placeholder: str) -> None: ...
```

### extractPlaceholders / extract_placeholders

Extract and trim placeholders from a template.

**TypeScript**
```typescript
import { extractPlaceholders } from '@internal/runtime-template-resolver';

extractPlaceholders(template: string): string[];
```

**Python**
```python
from runtime_template_resolver import extract_placeholders

def extract_placeholders(template: str) -> List[str]: ...
```

## Framework Integrations

### Fastify (Node.js)

```typescript
import fastifyTemplateResolver from '@internal/runtime-template-resolver/integrations/fastify-plugin';

await server.register(fastifyTemplateResolver, {
    missingStrategy: MissingStrategy.EMPTY
});

// In route handlers
const result = request.resolveTemplate('{{name}}', { name: 'World' });
```

### FastAPI (Python)

```python
from runtime_template_resolver.integrations.fastapi_utils import (
    create_resolver_dependency,
    ConfiguredResolverProtocol,
)

get_resolver = create_resolver_dependency()

@app.get("/resolve")
def endpoint(resolver: ConfiguredResolverProtocol = Depends(get_resolver)):
    return resolver.resolve("{{name}}", {"name": "World"})
```
