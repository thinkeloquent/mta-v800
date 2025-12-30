# Polyglot Server API Reference

## Core Components

### Init
Initialize the native server instance (FastAPI or Fastify) with the provided configuration.

**TypeScript**
```typescript
/**
 * Initialize and return native Fastify instance.
 * @param config Server configuration object
 */
export function init(config: ServerConfig): FastifyInstance;
```

**Python**
```python
def init(config: Dict[str, Any]) -> FastAPI:
    """Initialize and return native FastAPI instance."""
    ...
```

### Start
Start the server bootstrap sequence, load environment/lifecycle modules, and begin listening.

**TypeScript**
```typescript
/**
 * Start server with bootstrap configuration.
 * Loads env/lifecycle modules, runs startup hooks, and calls server.listen()
 */
export async function start(server: FastifyInstance, config: ServerConfig): Promise<void>;
```

**Python**
```python
async def start(server: FastAPI, config: Dict[str, Any]) -> None:
    """
    Start server with bootstrap configuration.
    Loads env/lifecycle modules, runs startup hooks, and runs Uvicorn.
    """
    ...
```

### Stop
Gracefully stop the server.

**TypeScript**
```typescript
export async function stop(server: FastifyInstance, config: ServerConfig): Promise<void>;
```

**Python**
```python
async def stop(server: FastAPI, config: Dict[str, Any]) -> None:
    """Gracefully stop the server."""
    ...
```

## Configuration Structures

### ServerConfig
The configuration object passed to `init` and `start`.

**TypeScript**
```typescript
interface ServerConfig {
  title?: string;
  host?: string;
  port?: number | string;
  log_level?: string; // 'debug' | 'info' | 'warn' | 'error'
  bootstrap?: {
    load_env?: string;   // Path to env loading modules
    lifecycle?: string;  // Path to lifecycle modules
  };
  initial_state?: Record<string, any>; // State deep-cloned to every request
}
```

**Python**
```python
# Type hint typical structure
class ServerConfig(TypedDict, total=False):
    title: str
    host: str
    port: Union[int, str]
    log_level: str
    bootstrap: Dict[str, str]  # keys: load_env, lifecycle
    initial_state: Dict[str, Any] # State deep-copied to every request
```

## Logger

### LoggerFactory
Standardized logger factory ensuring consistent formatting and context.

**TypeScript**
```typescript
const log = logger.create("package_name", import.meta.url);
log.info("Message", { data: "value" });
```

**Python**
```python
from logger import logger
log = logger.create("package_name", __file__)
log.info("Message", {"data": "value"})
```
