# Behavioral Differences

This document outlines intentional differences between the Node.js and Python implementations of the App YAML Static Config package.

## 1. Initialization Pattern

| Language | Pattern | Signature |
|----------|---------|-----------|
| **Node.js** | Async/await | `static async initialize(options: InitOptions): Promise<AppYamlConfig>` |
| **Python** | Synchronous | `@classmethod def initialize(cls, options: InitOptions) -> 'AppYamlConfig'` |

**Reasoning**: Node.js uses async/await for consistency with the ecosystem's asynchronous patterns, even though file reading in this implementation is synchronous. Python follows the synchronous convention standard for configuration loading.

## 2. Nested Key Access

| Language | Parameter Style | Signature |
|----------|-----------------|-----------|
| **Node.js** | Array parameter | `getNested<T>(keys: string[], defaultValue?: T): T \| undefined` |
| **Python** | Variadic args | `def get_nested(self, *keys: str, default: Any = None) -> Any` |

**Reasoning**: Node.js uses an array parameter which is idiomatic for JavaScript/TypeScript. Python uses variadic arguments (`*keys`) which allows for cleaner call syntax: `get_nested("app", "name")` vs `getNested(["app", "name"])`.

## 3. Naming Conventions

| Language | Property Names | Method Names |
|----------|---------------|--------------|
| **Node.js** | camelCase | `configDir`, `getNested`, `getAll` |
| **Python** | snake_case | `config_dir`, `get_nested`, `get_all` |

**Reasoning**: Each implementation follows language-specific conventions. TypeScript uses camelCase per JavaScript standards, while Python uses snake_case per PEP 8.

## 4. Original Configs Storage

| Language | Data Structure | Return Type |
|----------|---------------|-------------|
| **Node.js** | `Map<string, Record<string, any>>` | `Map<string, Record<string, any>>` |
| **Python** | `Dict[str, Dict[str, Any]]` | `Dict[str, Dict[str, Any]]` |

**Reasoning**: Node.js uses the native `Map` type which provides better key handling for file paths. Python uses the standard `dict` type which is the idiomatic choice for key-value storage.

## 5. SDK Factory Method

| Language | Pattern | Signature |
|----------|---------|-----------|
| **Node.js** | Async factory | `static async fromDirectory(configDir: string): Promise<AppYamlConfigSDK>` |
| **Python** | Sync factory | `@classmethod def from_directory(cls, config_dir: str) -> 'AppYamlConfigSDK'` |

**Reasoning**: Matches the initialization pattern difference. Node.js uses async for glob operations, while Python handles file discovery synchronously.

## 6. Deep Merge Implementation

| Language | Implementation | Library |
|----------|---------------|---------|
| **Node.js** | External library | `lodash.merge` |
| **Python** | Custom method | `_deep_merge()` |

**Reasoning**: Node.js leverages the well-tested `lodash.merge` for deep object merging. Python implements a custom recursive merge to avoid external dependencies for a simple operation.

## 7. Deep Clone Implementation

| Language | Implementation | Method |
|----------|---------------|--------|
| **Node.js** | Native API | `structuredClone()` |
| **Python** | Standard library | `copy.deepcopy()` |

**Reasoning**: Both implementations use the idiomatic approach for their respective languages. Node.js uses the modern `structuredClone()` API, while Python uses `copy.deepcopy()`.

## 8. Immutability Stub Return Types

| Language | Return Type | Throws |
|----------|-------------|--------|
| **Node.js** | `never` | `ImmutabilityError` |
| **Python** | `None` (raises) | `ImmutabilityError` |

**Reasoning**: TypeScript's `never` type explicitly indicates the method never returns normally. Python's type hints don't have an equivalent, so `None` is used with the understanding that the method always raises.
