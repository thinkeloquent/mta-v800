# Server Integration Guide for Vault File

This guide describes how to integrate the Vault File package with Fastify (Node.js) and FastAPI (Python) servers.

## Fastify Integration (Node.js)

The integration uses `EnvStore.onStartup()` during the Fastify plugin registration phase to ensure environment variables are loaded before the server starts accepting requests.

### Pattern: Fastify Plugin

```typescript
import fp from 'fastify-plugin';
import { EnvStore, LoadResult } from '@internal/vault-file';

export const vaultFilePlugin = fp(async (fastify, opts) => {
  // Load environment variables early in the plugin chain
  const result: LoadResult = await EnvStore.onStartup();
  
  fastify.log.info({ totalVars: result.totalVarsLoaded }, 'Vault File loaded');
  
  // Decorate fastify if needed, or rely on EnvStore singleton
  // fastify.decorate('env', EnvStore); 
});
```

### Usage

```typescript
import Fastify from 'fastify';
import { vaultFilePlugin } from './plugins/vault-file';

const server = Fastify();

server.register(vaultFilePlugin);

await server.ready();
```

## FastAPI Integration (Python)

The integration uses the `lifespan` context manager in FastAPI to load environment variables during application startup.

### Pattern: Lifespan Context Manager

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from vault_file import EnvStore

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    result = EnvStore.on_startup()
    print(f"Vault File loaded: {result.total_vars_loaded} vars")
    yield
    # Shutdown logic (if any)

app = FastAPI(lifespan=lifespan)
```
