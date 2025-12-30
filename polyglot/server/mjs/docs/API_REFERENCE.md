# Node.js Server API Reference

## Module: src/server.mjs

### `init(config: ServerConfig): FastifyInstance`
Initialize and return the native Fastify instance.

- **config**: Configuration object.
  - `title`: Application title.
  - `logger`: Fastify logger configuration (defaults to true).
- **Returns**: Fastify server instance.

### `async start(server: FastifyInstance, config: ServerConfig): Promise<void>`
Start server with bootstrap configuration.

- **server**: Fastify instance.
- **config**: Configuration object.
  - `bootstrap.load_env`: Path to directory containing environment modules (`*.mjs`).
  - `bootstrap.lifecycle`: Path to directory containing lifecycle modules (`*.mjs`).
  - `initial_state`: Object to be structured-cloned to `request.state` for every request.
  - `host`: Host to bind (default: 0.0.0.0).
  - `port`: Port to bind (default: 8080 or process.env.PORT).

**Behavior**:
1. **Bootstrap**: Loads environment and lifecycle modules via dynamic `import()`.
2. **Hooks**: Registers `onStartup` (executed immediately) and `onShutdown` (registered to `onClose`).
3. **Request State**: If `initial_state` is present, decorates request with `state` and registers `onRequest` hook to clone it using `structuredClone`.
4. **Shutdown**: Registers `close-with-grace` to handle SIGINT/SIGTERM and trigger graceful `server.close()`.
5. **Execution**: Calls `server.listen()`.

### `async stop(server: FastifyInstance, config: ServerConfig): Promise<void>`
Gracefully stop the server. Calls `server.close()`.

## Module: src/logger.mjs

### `create(packageName: string, filename: string, options?: LoggerConfig): Logger`
Factory function to create a standardized logger instance.

```typescript
import logger from './logger.mjs';
const log = logger.create("myservice", import.meta.url);
```

### Interface `Logger`
Provides standard logging methods: `debug`, `info`, `warn`, `error`, `trace`.

#### Methods
- **child(filename: string, options?: LoggerConfig)**: Create a child logger.
- **withContext(context: object)**: Create a context logger merging data.
