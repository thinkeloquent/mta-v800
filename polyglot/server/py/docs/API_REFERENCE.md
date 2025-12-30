# Python Server API Reference

## Module: app.server

### `init(config: Dict[str, Any]) -> FastAPI`
Initialize and return the native FastAPI instance.

- **config**: Dictionary containing server configuration.
  - `title`: Application title.
  - `initial_state`: Dictionary to be deep-copied to `request.state` for every request.
- **Returns**: A configured `FastAPI` application instance with `lifespan` context manager configured.

### `async start(server: FastAPI, config: Dict[str, Any]) -> None`
Start server with bootstrap configuration.

- **server**: The FastAPI instance created by `init`.
- **config**: Configuration dictionary.
  - `bootstrap.load_env`: Path to directory containing environment variable loading modules (`*.py`).
  - `bootstrap.lifecycle`: Path to directory containing lifecycle modules (`*.py`).
  - `host`: Host to bind (default: 0.0.0.0).
  - `port`: Port to bind (default: 8080).
  - `log_level`: Uvicorn log level.

**Behavior**:
1. **Bootstrap**: Loads environment and lifecycle modules via `importlib`.
2. **Hooks**: Registers `startup_hooks` and `shutdown_hooks` from lifecycle modules.
3. **Middleware**: If `initial_state` is present, registers HTTP middleware to deep-copy state to `request.state`.
4. **Execution**: Configures and runs `uvicorn.Server`.

### `async stop(server: FastAPI, config: Dict[str, Any]) -> None`
Gracefully stop the server.
- **Note**: When running with Uvicorn, shutdown is typically handled via signals (SIGTERM/SIGINT) which trigger the lifespan context exit.

## Module: app.logger

### `create(package_name: str, filename: str, ...) -> Logger`
Factory method to create a standardized logger instance.

```python
from logger import logger
log = logger.create("myservice", __file__)
```

### Class `Logger`
Provides standard logging methods: `debug`, `info`, `warn`, `error`, `trace`.

#### Methods
- **child(filename: str, \*\*kwargs)**: Create a child logger sharing configuration.
- **with_context(context: Dict)**: Create a context logger that merges data into every log.
