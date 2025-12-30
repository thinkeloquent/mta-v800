# Server Integration Guide for Polyglot Server

This guide describes how to integrate the Polyglot Server scaffolding into your Fastify or FastAPI applications.

## Fastify Integration (Node.js)

The server integration manages distinct phases: Bootstrap (Env/Lifecycle), Init, and Start.

### Standard Usage

In `src/main.mjs`:

```typescript
import * as server from "./server.mjs";

const config = {
  title: "My Polyglot App",
  port: process.env.PORT || 8080,
  bootstrap: {
    load_env: "./config/env",
    lifecycle: "./config/lifecycle"
  }
};

try {
  // 1. Init
  const app = server.init(config);
  
  // 2. Start (Bootstrap + Listen)
  await server.start(app, config);
  
} catch (err) {
  console.error(err);
  process.exit(1);
}
```

## FastAPI Integration (Python)

The integration relies on Uvicorn for execution, with the `server` module wrapping the configuration.

### Standard Usage

In `app/main.py`:

```python
import asyncio
from server import init, start

config = {
    "title": "My Polyglot App",
    "port": 8080,
    "bootstrap": {
        "load_env": "./config/env",
        "lifecycle": "./config/lifecycle"
    }
}

if __name__ == "__main__":
    # 1. Init
    app = init(config)
    
    # 2. Start (Bootstrap + Serve)
    asyncio.run(start(app, config))
```
