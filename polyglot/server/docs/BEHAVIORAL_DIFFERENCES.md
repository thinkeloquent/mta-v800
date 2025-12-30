# Behavioral Differences

This document outlines intentional differences between the Node.js (Fastify) and Python (FastAPI) implementations of the Polyglot Server.

## 1. Startup Hook Execution

| Language | Execution Point | Mechanism |
|----------|-----------------|-----------|
| **Node.js** | Before `server.listen()` | Explicit iteration and `await hook(server, config)` call. |
| **Python** | Inside Uvicorn Lifespan | `asynccontextmanager` yielding control to Uvicorn. |

**Reasoning**: Node.js's Fastify separates initialization from listening more explicitly in established patterns. Python's FastAPI/Uvicorn strongly prefers the ASGI strict lifespan protocol for correct resource management.

## 2. Request State Cloning

| Language | Cloning Method | Hooks |
|----------|----------------|-------|
| **Node.js** | `structuredClone` | `onRequest` hook. |
| **Python** | `copy.deepcopy` | `@server.middleware("http")` |

**Reasoning**: `structuredClone` is the modern standard for deep copying in Node.js/Browser. Python uses `copy.deepcopy` as the standard library equivalent. Both achieve the goal of isolating initial state per request.

## 3. Graceful Shutdown

| Language | Mechanism | Dependency |
|----------|-----------|------------|
| **Node.js** | `close-with-grace` wrapper | `close-with-grace` npm package. |
| **Python** | Uvicorn Signal Handlers | Built-in Uvicorn signal handling. |

**Reasoning**: Uvicorn has robust built-in signal handling for ASGI apps. Node.js required an external library (`close-with-grace`) to robustly handle SIGINT/SIGTERM and ensure async cleanup (hooks) completes before process exit.

## 4. Environment Loading

| Language | Implementation |
|----------|----------------|
| **Node.js** | Dynamic `import()` of `.mjs` files found via `glob`. |
| **Python** | `importlib.util` dynamic loading of `.py` files found via `pathlib`. |

**Reasoning**: Native dynamic import mechanisms for each language.
