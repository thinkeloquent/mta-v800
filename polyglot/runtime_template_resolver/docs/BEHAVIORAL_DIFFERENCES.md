# Behavioral Differences

This document outlines intentional differences between the Node.js and Python implementations of the Runtime Template Resolver package.

## 1. Naming Conventions

Method and property names follow language-idiomatic conventions.

| Language | Style | Example Method | Example Option |
|----------|-------|----------------|----------------|
| **Node.js** | camelCase | `resolveObject()` | `missingStrategy` |
| **Python** | snake_case | `resolve_object()` | `missing_strategy` |

**Reasoning**: Each language has established naming conventions (PEP 8 for Python, JavaScript style guides for Node.js). Following these conventions ensures the API feels native to developers in each language.

## 2. SDK Access Pattern

The SDK functions are accessed differently in each language.

| Language | Pattern | Example |
|----------|---------|---------|
| **Node.js** | Static class methods | `SDK.resolve(template, context)` |
| **Python** | Module-level functions | `resolve(template, context)` |

**Reasoning**: TypeScript/JavaScript commonly uses static class patterns for namespacing, while Python idiomatically uses module-level functions that are imported directly.

**Node.js**
```typescript
import { SDK } from '@internal/runtime-template-resolver';
const result = SDK.resolve('{{name}}', context);
```

**Python**
```python
from runtime_template_resolver import resolve
result = resolve("{{name}}", context)
```

## 3. Options Passing

Configuration options are passed differently to methods.

| Language | Pattern | Example |
|----------|---------|---------|
| **Node.js** | Object parameter | `resolve(template, context, { missingStrategy: ... })` |
| **Python** | Named parameter | `resolve(template, context, options=ResolverOptions(...))` |

**Reasoning**: JavaScript uses plain objects for options (duck typing), while Python uses explicit dataclasses for better type safety and IDE support.

## 4. Boolean Coercion in Output

Boolean values are coerced to strings differently.

| Language | `true` | `false` |
|----------|--------|---------|
| **Node.js** | `"true"` | `"false"` |
| **Python** | `"True"` | `"False"` |

**Reasoning**: Each language uses its native string representation of boolean values. JavaScript uses lowercase (`true`/`false`), while Python uses title case (`True`/`False`).

## 5. Object/Dict Coercion in Output

When a placeholder resolves to an object/dict, the string representation differs.

| Language | Output Format |
|----------|---------------|
| **Node.js** | JSON string: `{"name":"Alice"}` |
| **Python** | Python repr: `{'name': 'Alice'}` or JSON |

**Reasoning**: Node.js uses `JSON.stringify()` for consistent output, while Python may use `str()` which produces Python-style dict representation. Both implementations ensure objects are coerced to strings rather than causing errors.

## 6. Framework Integration Patterns

Integration with web frameworks follows different patterns.

| Language | Framework | Pattern |
|----------|-----------|---------|
| **Node.js** | Fastify | Plugin with request decorator |
| **Python** | FastAPI | Dependency injection with protocol |

**Reasoning**: Each framework has its own idiomatic patterns for extension. Fastify uses plugins and decorators, while FastAPI uses dependency injection.

**Node.js (Fastify)**
```typescript
await server.register(fastifyTemplateResolver);

server.get('/test', (request) => {
    return request.resolveTemplate('{{name}}', context);
});
```

**Python (FastAPI)**
```python
get_resolver = create_resolver_dependency()

@app.get("/test")
def endpoint(resolver = Depends(get_resolver)):
    return resolver.resolve("{{name}}", context)
```

## 7. Error Handling

Errors are handled using language-appropriate mechanisms.

| Language | Error Type | Handling |
|----------|------------|----------|
| **Node.js** | Classes extending `Error` | `try/catch` with `instanceof` |
| **Python** | Classes extending `Exception` | `try/except` with exception types |

**Reasoning**: Both languages have different exception handling idioms and conventions for custom error classes.

**Node.js**
```typescript
try {
    SDK.resolve('{{_private}}', {}, { throwOnError: true });
} catch (e) {
    if (e instanceof SecurityError) {
        console.error('Security error:', e.message);
    }
}
```

**Python**
```python
try:
    resolve("{{_private}}", {}, options=ResolverOptions(throw_on_error=True))
except SecurityError as e:
    print(f"Security error: {e}")
```

## 8. Async/Sync Patterns

Both implementations are synchronous, but integration patterns may differ.

| Language | Core API | Framework Integration |
|----------|----------|----------------------|
| **Node.js** | Sync | Works in async handlers |
| **Python** | Sync | Works in async handlers |

**Reasoning**: Template resolution is a CPU-bound operation that doesn't benefit from async patterns. Both implementations are synchronous but can be used within async framework handlers.

## 9. Module Exports

The module structure and exports follow language conventions.

| Language | Export Style |
|----------|--------------|
| **Node.js** | Named exports + default SDK |
| **Python** | `__all__` in `__init__.py` |

**Reasoning**: Each language has different conventions for module organization and exports.

**Node.js**
```typescript
export { TemplateResolver, SDK, MissingStrategy, ... };
export default SDK;
```

**Python**
```python
__all__ = [
    "TemplateResolver",
    "resolve",
    "MissingStrategy",
    ...
]
```

## 10. Type System Integration

Type definitions are provided differently.

| Language | Type System | Location |
|----------|-------------|----------|
| **Node.js** | TypeScript | Source files (`.ts`) |
| **Python** | Type hints | Source files + `py.typed` marker |

**Reasoning**: TypeScript has native type support, while Python uses type hints (PEP 484) with a marker file for typed packages.

## Summary Table

| Aspect | Node.js | Python |
|--------|---------|--------|
| Naming | camelCase | snake_case |
| SDK access | `SDK.method()` | `function()` |
| Options | Object literal | Dataclass |
| Booleans | `"true"`/`"false"` | `"True"`/`"False"` |
| Framework | Fastify plugin | FastAPI dependency |
| Errors | `Error` subclass | `Exception` subclass |
| Types | TypeScript | Type hints |
