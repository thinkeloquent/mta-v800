# Behavioral Differences

This document outlines intentional differences between the Node.js and Python implementations of the Vault File package.

## 1. EnvStore Priority

The priority for resolving environment variables differs to match language-idiomatic patterns:

| Language | Priority Order | Rationale |
|----------|----------------|-----------|
| **Node.js** | `process.env` > Internal Store | Standard Node.js behavior is that process environment variables take precedence over loaded .env files. |
| **Python** | Internal Store > `os.environ` | Allows the application configuration to explicitly override system environment variables if needed. |

## 2. Startup Pattern via EnvStore

| Language | Pattern | Signature |
|----------|---------|-----------|
| **Node.js** | Async | `static async onStartup(): Promise<LoadResult>` |
| **Python** | Synchronous | `classmethod on_startup() -> LoadResult` |

**Reasoning**: Node.js file I/O is asynchronous by default, while Python's `open()` is synchronous and typically acceptable during startup.

## 3. Serialization Field Naming

Internally, each language uses its idiomatic naming convention. When serialized to JSON, all fields are normalized to `snake_case`.

| Field | Node.js (Internal) | Python (Internal) | JSON (Serialized) |
|-------|--------------------|-------------------|-------------------|
| Created At | `createdAt` | `created_at` | `created_at` |
| Vars Loaded | `totalVarsLoaded` | `total_vars_loaded` | `totalVarsLoaded` (LoadResult) |

**Note**: `LoadResult` uses camelCase `totalVarsLoaded` in JSON to match the domain model definition parity in Phase 1-2 decisions.
