# Behavioral Differences

This document outlines intentional differences between the Node.js and Python implementations of the Runtime Template Resolver package.

## 1. Naming Conventions

Property and method names follow language-idiomatic conventions.

| Language | Style | Example |
|----------|-------|---------|
| **Node.js** | camelCase | `maxDepth`, `resolveObject`, `getScope` |
| **Python** | snake_case | `max_depth`, `resolve_object`, `get_scope` |

**Reasoning**: Each language has established naming conventions (PEP 8 for Python, standard JS conventions for Node.js). Following idiomatic patterns makes the SDK feel native to developers in each ecosystem.

## 2. Async/Await Patterns

Both implementations are async, but with subtle differences in how async is handled.

| Language | Pattern | Signature |
|----------|---------|-----------|
| **Node.js** | Always async | `async resolve(): Promise<any>` |
| **Python** | Always async | `async def resolve() -> Any` |

**Reasoning**: Template resolution may involve I/O operations (file reads, network calls) in compute functions. Both implementations use async/await consistently to support these use cases without blocking.

## 3. Context Path Resolution

The method used to traverse nested objects differs between implementations.

| Language | Library | Method |
|----------|---------|--------|
| **Node.js** | lodash | `_.get(context, 'path.to.value')` |
| **Python** | native | Custom `_get_value_by_path()` implementation |

**Reasoning**: Node.js leverages lodash's battle-tested `get` function for safe nested property access. Python uses a native implementation to avoid additional dependencies while maintaining the same behavior.

## 4. Options Structure

Configuration options use different patterns.

| Language | Pattern | Definition |
|----------|---------|------------|
| **Node.js** | Interface | `interface ResolverOptions { ... }` |
| **Python** | Dataclass | `@dataclass class ResolverOptions: ...` |

**Reasoning**: TypeScript interfaces provide type safety at compile time, while Python dataclasses provide runtime type hints and automatic `__init__` generation. Both approaches are idiomatic for their respective ecosystems.

## 5. Enum Definition

Enums are defined differently but represent the same values.

| Language | Pattern | Access |
|----------|---------|--------|
| **Node.js** | TypeScript enum | `ComputeScope.STARTUP` |
| **Python** | Python Enum class | `ComputeScope.STARTUP` |

**Reasoning**: Both use native enum constructs. TypeScript enums compile to JavaScript objects, while Python Enums are true class-based enumerations with additional features like iteration.

## 6. Error Context Properties

Error context properties follow naming conventions.

| Language | Property | Example |
|----------|----------|---------|
| **Node.js** | camelCase | `{ name, originalError, fnScope }` |
| **Python** | snake_case | `{ "name", "original_error", "fn_scope" }` |

**Reasoning**: Error context objects follow the same naming conventions as the rest of the codebase for consistency.

## 7. Logger Integration

Default logger behavior and naming.

| Language | Default Logger Name | Method |
|----------|---------------------|--------|
| **Node.js** | `'runtime-template-resolver'` | `Logger.create(name, filename)` |
| **Python** | `'runtime_template_resolver'` | `Logger.create(name, __file__)` |

**Reasoning**: Logger names follow package naming conventions (hyphenated for npm, underscored for PyPI).

## 8. Framework Integration

Server framework integrations use idiomatic patterns.

| Language | Framework | Pattern |
|----------|-----------|---------|
| **Node.js** | Fastify | Plugin with `fastify-plugin` wrapper |
| **Python** | FastAPI | Lifespan context manager + dependencies |

**Reasoning**: Each framework has established patterns for initialization and request handling. Fastify uses plugins; FastAPI uses lifespan managers and dependency injection.

## 9. Type Coercion in Default Values

Slight differences in numeric type detection.

| Language | `'42'` | `'3.14'` | Detection Method |
|----------|--------|----------|------------------|
| **Node.js** | `42` (number) | `3.14` (number) | `!isNaN(Number(val))` |
| **Python** | `42` (int) | `3.14` (float) | `isdigit()` then `float()` |

**Reasoning**: Node.js uses JavaScript's single `number` type. Python distinguishes between `int` and `float`, so the implementation checks for integers first before falling back to float parsing.

## 10. Cache Implementation

Internal caching uses native data structures.

| Language | Structure | Access Pattern |
|----------|-----------|----------------|
| **Node.js** | `Map<string, any>` | `this.cache.get(name)` |
| **Python** | `Dict[str, Any]` | `self._cache[name]` |

**Reasoning**: Both use their language's idiomatic hash map implementation. ES6 Map provides consistent key ordering and better performance for frequent additions/deletions. Python dicts (3.7+) maintain insertion order.

## 11. Function Registration Validation

Function name validation pattern is identical.

| Language | Pattern | Validation |
|----------|---------|------------|
| **Node.js** | `/^[a-zA-Z_][a-zA-Z0-9_]*$/` | `test()` method |
| **Python** | `r'^[a-zA-Z_][a-zA-Z0-9_]*$'` | `match()` method |

**Reasoning**: Both use the same regex pattern to ensure function names are valid identifiers. This prevents injection attacks and ensures consistency across implementations.

## Summary

The Runtime Template Resolver maintains functional parity between Node.js and Python while respecting the idioms and conventions of each ecosystem. Code written for one platform should be conceptually portable to the other with straightforward syntax translation.
