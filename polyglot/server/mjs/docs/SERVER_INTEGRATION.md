# Server Integration Guide for Fastify

## Fastify Integration (Node.js)

The integration manages distinct phases: Bootstrap (Env/Lifecycle), Init, and Start.

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

### Graceful Shutdown

The server integration uses `close-with-grace` to intercept `SIGINT` and `SIGTERM` signals.
This ensures that `onClose` hooks (registered during bootstrap) are executed before the process exits.

```typescript
// Internal implementation detail
closeWithGrace({ delay: 30000 }, async ({ signal, err }) => {
    // Calls server.close() which triggers onClose hooks
    await server.close();
});
```
