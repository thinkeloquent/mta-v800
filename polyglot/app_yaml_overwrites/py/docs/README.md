# app_yaml_overwrites (Python)

Unified Configuration SDK for Python applications. Provides standardized logging, context building, and configuration merging for FastAPI and other Python frameworks.

## Installation

```bash
# Install package
pip install app-yaml-overwrites

# Install with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

### Logger

```python
from app_yaml_overwrites.logger import Logger

logger = Logger.create('my-service', 'main.py')

logger.info('Application started', version='1.0.0')
logger.error('Connection failed', host='localhost', error='timeout')
```

### Context Builder

```python
from app_yaml_overwrites.context_builder import ContextBuilder

async def auth_extender(ctx, request):
    return {'auth': {'user_id': 'user-123'}}

context = await ContextBuilder.build(
    {'config': config, 'app': app_info},
    extenders=[auth_extender]
)
```

### Overwrite Merger

```python
from app_yaml_overwrites.overwrite_merger import apply_overwrites

resolved = apply_overwrites(
    original_config,
    config.get('overwrite_from_context', {})
)
```

### FastAPI Integration

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app_yaml_overwrites import ConfigSDK

@asynccontextmanager
async def lifespan(app: FastAPI):
    sdk = await ConfigSDK.initialize()
    app.state.config = sdk.get_raw()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/health')
async def health():
    return {'status': 'healthy', 'app': app.state.config['app']['name']}
```

## Features

- **Logger**: JSON-structured logging with `LOG_LEVEL` control
- **ContextBuilder**: Build resolution context with async extenders
- **OverwriteMerger**: Deep merge `overwrite_from_context` sections
- **ConfigSDK**: High-level singleton for configuration management

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `debug` | Logging level: `trace`, `debug`, `info`, `warn`, `error` |

## Documentation

- [API Reference](./API_REFERENCE.md) - Complete Python API
- [Examples](../examples/) - Working example code
- [Common Docs](../../docs/) - Cross-language documentation

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest __tests__/ -v

# Run tests with coverage
pytest __tests__/ -v --cov=src/app_yaml_overwrites
```

## Project Structure

```
py/
├── src/
│   └── app_yaml_overwrites/
│       ├── __init__.py
│       ├── logger.py
│       ├── context_builder.py
│       ├── overwrite_merger.py
│       ├── sdk.py
│       └── cli.py
├── __tests__/
│   ├── conftest.py
│   ├── test_logger.py
│   ├── test_context_builder.py
│   ├── test_overwrite_merger.py
│   └── test_sdk.py
├── examples/
│   ├── basic_usage.py
│   └── fastapi_app/
├── docs/
│   ├── README.md
│   └── API_REFERENCE.md
└── pyproject.toml
```

## License

See repository root for license information.
