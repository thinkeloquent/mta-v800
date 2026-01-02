# Runtime Template Resolver API Reference

Complete API reference for the Runtime Template Resolver package, showing type signatures and interfaces for both TypeScript and Python implementations.

## Core Components

### ComputeScope

Defines when compute functions are executed and cached.

**TypeScript**
```typescript
enum ComputeScope {
    STARTUP = 'STARTUP',   // Cached at application startup
    REQUEST = 'REQUEST'    // Executed per-request, not cached
}
```

**Python**
```python
class ComputeScope(Enum):
    STARTUP = "STARTUP"   # Cached at application startup
    REQUEST = "REQUEST"   # Executed per-request, not cached
```

### MissingStrategy

Controls behavior when a template variable or compute function is not found.

**TypeScript**
```typescript
enum MissingStrategy {
    ERROR = 'ERROR',      // Raise an error
    DEFAULT = 'DEFAULT',  // Return undefined/None
    IGNORE = 'IGNORE'     // Return the original pattern string
}
```

**Python**
```python
class MissingStrategy(Enum):
    ERROR = "ERROR"       # Raise an error
    DEFAULT = "DEFAULT"   # Return None
    IGNORE = "IGNORE"     # Return the original pattern string
```

### ResolverOptions

Configuration options for the ContextResolver.

**TypeScript**
```typescript
interface ResolverOptions {
    logger?: Logger;
    maxDepth?: number;           // Default: 10
    missingStrategy?: MissingStrategy;  // Default: ERROR
}
```

**Python**
```python
@dataclass
class ResolverOptions:
    max_depth: int = 10
    missing_strategy: MissingStrategy = MissingStrategy.ERROR
    logger: Optional[Logger] = None
```

### ComputeRegistry

Registry for compute functions that can be invoked via `{{fn:name}}` patterns.

**TypeScript**
```typescript
class ComputeRegistry {
    constructor(logger?: Logger);

    register(name: string, fn: ComputeFunction, scope: ComputeScope): void;
    unregister(name: string): void;
    has(name: string): boolean;
    list(): string[];
    getScope(name: string): ComputeScope | undefined;
    clear(): void;
    clearCache(): void;
    resolve(name: string, context?: any): Promise<any>;
}

type ComputeFunction = (context?: any) => any | Promise<any>;
```

**Python**
```python
class ComputeRegistry:
    def __init__(self, logger: Optional[Logger] = None): ...

    def register(self, name: str, fn: Callable, scope: ComputeScope) -> None: ...
    def unregister(self, name: str) -> None: ...
    def has(self, name: str) -> bool: ...
    def list(self) -> List[str]: ...
    def get_scope(self, name: str) -> Optional[ComputeScope]: ...
    def clear(self) -> None: ...
    def clear_cache(self) -> None: ...
    async def resolve(self, name: str, context: Optional[Dict[str, Any]] = None) -> Any: ...
```

### ContextResolver

Main resolver class for template and compute pattern resolution.

**TypeScript**
```typescript
class ContextResolver {
    constructor(registry: ComputeRegistry, options?: ResolverOptions);

    isComputePattern(expression: string): boolean;

    resolve(
        expression: any,
        context: Record<string, any>,
        scope?: ComputeScope,
        depth?: number
    ): Promise<any>;

    resolveObject(
        obj: any,
        context: Record<string, any>,
        scope?: ComputeScope,
        depth?: number
    ): Promise<any>;

    resolveMany(
        expressions: any[],
        context: Record<string, any>,
        scope?: ComputeScope
    ): Promise<any[]>;
}
```

**Python**
```python
class ContextResolver:
    def __init__(
        self,
        registry: ComputeRegistry,
        options: Optional[ResolverOptions] = None
    ): ...

    def is_compute_pattern(self, expression: str) -> bool: ...

    async def resolve(
        self,
        expression: Any,
        context: Dict[str, Any],
        scope: ComputeScope = ComputeScope.REQUEST,
        depth: int = 0
    ) -> Any: ...

    async def resolve_object(
        self,
        obj: Any,
        context: Dict[str, Any],
        scope: ComputeScope = ComputeScope.REQUEST,
        depth: int = 0
    ) -> Any: ...

    async def resolve_many(
        self,
        expressions: List[Any],
        context: Dict[str, Any],
        scope: ComputeScope = ComputeScope.REQUEST
    ) -> List[Any]: ...
```

### Security

Static utility class for path validation to prevent prototype pollution and path traversal attacks.

**TypeScript**
```typescript
class Security {
    static validatePath(path: string): void;  // Throws SecurityError if invalid
}
```

**Python**
```python
class Security:
    @classmethod
    def validate_path(cls, path: str) -> None: ...  # Raises SecurityError if invalid
```

## SDK

Factory functions for creating resolver instances.

**TypeScript**
```typescript
import { createRegistry, createResolver } from 'runtime-template-resolver';

// Create a registry for compute functions
const registry = createRegistry(logger?);

// Create a resolver with optional registry and options
const resolver = createResolver(registry?, options?, logger?);
```

**Python**
```python
from runtime_template_resolver import create_registry, create_resolver

# Create a registry for compute functions
registry = create_registry(logger=None)

# Create a resolver with optional registry and options
resolver = create_resolver(registry=None, options=None, logger=None)
```

### SDK Operations

- `createRegistry(logger?)` / `create_registry(logger)`: Create a new ComputeRegistry instance
- `createResolver(registry?, options?, logger?)` / `create_resolver(registry, options, logger)`: Create a new ContextResolver instance

## Error Classes

All errors extend from `ResolveError` base class.

**TypeScript**
```typescript
class ResolveError extends Error {
    code: string;
    context: Record<string, any>;
}

class ComputeFunctionError extends ResolveError {}
class SecurityError extends ResolveError {}
class RecursionLimitError extends ResolveError {}
class ScopeViolationError extends ResolveError {}
class ValidationError extends ResolveError {}
```

**Python**
```python
class ResolveError(Exception):
    code: str
    context: dict

class ComputeFunctionError(ResolveError): pass
class SecurityError(ResolveError): pass
class RecursionLimitError(ResolveError): pass
class ScopeViolationError(ResolveError): pass
class ValidationError(ResolveError): pass
```

### Error Codes

| Code | Description |
|------|-------------|
| `ERR_COMPUTE_NOT_FOUND` | Compute function not registered |
| `ERR_COMPUTE_FAILED` | Compute function execution failed |
| `ERR_SECURITY_PATH` | Path validation failed (blocked pattern or traversal) |
| `ERR_RECURSION_LIMIT` | Maximum resolution depth exceeded |
| `ERR_SCOPE_VIOLATION` | REQUEST function called from STARTUP scope |
| `ERR_VALIDATION_ERROR` | General validation error |

## Pattern Syntax

### Template Patterns

```
{{path.to.value}}                    - Resolve from context
{{path.to.value | 'default'}}        - With default value
```

### Compute Patterns

```
{{fn:function_name}}                 - Call registered function
{{fn:function_name | 'default'}}     - With default on failure
```

### Default Value Type Inference

Default values are automatically parsed:

| Pattern | Resolved Type |
|---------|---------------|
| `'true'` | `boolean` (true) |
| `'false'` | `boolean` (false) |
| `'42'` | `number` (42) |
| `'3.14'` | `number` (3.14) |
| `'hello'` | `string` ("hello") |
