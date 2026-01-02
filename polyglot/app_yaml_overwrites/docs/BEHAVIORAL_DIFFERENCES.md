# Behavioral Differences

This document outlines intentional differences between the Node.js and Python implementations of the `app_yaml_overwrites` package. These differences reflect language idioms and ecosystem conventions while maintaining API parity.

## 1. Naming Conventions

Property and method names follow language-specific conventions.

| Language | Properties | Methods | Example |
|----------|------------|---------|---------|
| **Node.js** | camelCase | camelCase | `getRaw()`, `contextExtenders` |
| **Python** | snake_case | snake_case | `get_raw()`, `context_extenders` |

**Reasoning**: Each language has established naming conventions (PEP 8 for Python, standard JavaScript conventions). Following these makes the code feel native to developers in each ecosystem.

## 2. Logger Data Parameter

How additional data is passed to log methods differs.

| Language | Pattern | Signature |
|----------|---------|-----------|
| **Node.js** | Object parameter | `logger.info('message', { key: 'value' })` |
| **Python** | Keyword arguments | `logger.info('message', key='value')` |

**Reasoning**: Python's `**kwargs` pattern is idiomatic for passing optional named parameters, while JavaScript typically uses an options object.

## 3. Deep Merge Implementation

The underlying merge implementation differs.

| Language | Library | Behavior |
|----------|---------|----------|
| **Node.js** | lodash `_.merge` | Mutates first arg, merges arrays by index |
| **Python** | Custom recursive | Creates new dict, replaces arrays entirely |

**Reasoning**:
- Node.js uses lodash for its well-tested, performant merge
- Python implements a simple recursive merge to avoid external dependencies
- Array handling differs: lodash merges by index `[1,2,3] + [4,5] = [4,5,3]`, Python replaces entirely `[4,5]`

## 4. Singleton Pattern

The SDK singleton implementation differs slightly.

| Language | Pattern | Access |
|----------|---------|--------|
| **Node.js** | Private static property | `ConfigSDK.instance` (private) |
| **Python** | Class variable | `ConfigSDK._instance` (conventionally private) |

**Reasoning**: TypeScript enforces `private` access modifiers at compile time, while Python uses the `_` prefix convention for "private" attributes.

## 5. Async/Await Patterns

Both languages use async/await but with different syntax.

| Language | Async Function | Await Call |
|----------|----------------|------------|
| **Node.js** | `async function()` | `await promise` |
| **Python** | `async def` | `await coroutine` |

**Reasoning**: Standard language syntax. Both support async context extenders and async SDK initialization.

## 6. Type Annotations

Type definition approaches differ.

| Language | Type System | Runtime Enforcement |
|----------|-------------|---------------------|
| **Node.js** | TypeScript interfaces | Compile-time only |
| **Python** | Type hints (PEP 484) | Optional (mypy) |

**Reasoning**: TypeScript types are erased at compile time; Python type hints are metadata that can be checked with tools like mypy but aren't enforced at runtime by default.

## 7. Import Patterns

Module imports follow language conventions.

| Language | Pattern | Example |
|----------|---------|---------|
| **Node.js** | Named exports | `import { Logger } from './logger.js'` |
| **Python** | Module imports | `from .logger import Logger` |

**Reasoning**: ES modules vs Python's import system. Both support the same logical structure but with different syntax.

## 8. Error Handling

Exception types and handling differ.

| Language | Base Error | SDK Error |
|----------|------------|-----------|
| **Node.js** | `Error` | `new Error('ConfigSDK not initialized')` |
| **Python** | `Exception` | `RuntimeError('ConfigSDK not initialized')` |

**Reasoning**: Python uses more specific exception types (`RuntimeError` for runtime state errors) while JavaScript typically uses generic `Error`.

## 9. Context Builder Options

The options parameter structure differs slightly.

| Language | Options Type | Request Type |
|----------|--------------|--------------|
| **Node.js** | `ContextOptions` interface | `FastifyRequest` |
| **Python** | `Dict[str, Any]` | `Any` (duck-typed) |

**Reasoning**: TypeScript benefits from explicit interface definitions, while Python uses duck typing and dictionary access patterns.

## 10. Log Level Comparison

Log level handling implementation differs.

| Language | Level Source | Default |
|----------|--------------|---------|
| **Node.js** | `process.env.LOG_LEVEL` | `'debug'` |
| **Python** | `os.environ.get('LOG_LEVEL')` | `'debug'` |

**Reasoning**: Both read from environment, using language-specific APIs (`process.env` vs `os.environ`). Both default to `debug` level if not specified.

---

## Summary

The key principle is **API parity with idiomatic implementation**:

- Same logical operations available in both languages
- Same configuration patterns (`overwrite_from_context`)
- Same log output format (JSON)
- Language-native naming conventions
- Language-native async patterns
- Language-native error types

Developers can switch between languages knowing the concepts transfer directly, even if the exact syntax differs.
