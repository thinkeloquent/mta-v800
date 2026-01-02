# app_yaml_overwrites Python API Reference

This document provides the complete Python API reference for the `app_yaml_overwrites` package.

## Installation

```bash
pip install app-yaml-overwrites
# or with dev dependencies
pip install -e ".[dev]"
```

## Core Components

### Logger

```python
from app_yaml_overwrites.logger import Logger

class Logger:
    """
    Standardized JSON logger with structured output.

    Attributes:
        LEVELS: Dict mapping level names to logging integers
            - 'trace': 5
            - 'debug': 10 (logging.DEBUG)
            - 'info': 20 (logging.INFO)
            - 'warn': 30 (logging.WARNING)
            - 'error': 40 (logging.ERROR)
    """

    @classmethod
    def create(cls, package_name: str, filename: str) -> 'Logger':
        """
        Factory method to create a Logger instance.

        Args:
            package_name: Name of the package/service for context
            filename: Source filename for context

        Returns:
            Logger instance configured with the given context

        Example:
            logger = Logger.create('my-service', 'handler.py')
        """

    def debug(self, message: str, **kwargs) -> None:
        """Log debug-level message with optional data."""

    def info(self, message: str, **kwargs) -> None:
        """Log info-level message with optional data."""

    def warn(self, message: str, **kwargs) -> None:
        """Log warning-level message with optional data."""

    def error(self, message: str, **kwargs) -> None:
        """Log error-level message with optional data."""
```

#### Usage

```python
import os

# Set log level (optional, defaults to 'debug')
os.environ['LOG_LEVEL'] = 'info'

logger = Logger.create('my-service', 'main.py')

# Basic logging
logger.debug('Debug message')  # Suppressed when LOG_LEVEL=info
logger.info('Info message')
logger.warn('Warning message')
logger.error('Error message')

# With additional data (keyword arguments)
logger.info('Request processed', request_id='abc-123', duration_ms=150)
logger.error('Connection failed', host='localhost', port=5432, error='timeout')
```

#### Output Format

```json
{
    "timestamp": "2025-01-02T12:00:00.000000",
    "level": "INFO",
    "context": "my-service:main.py",
    "message": "Request processed",
    "data": {"request_id": "abc-123", "duration_ms": 150}
}
```

---

### ContextBuilder

```python
from app_yaml_overwrites.context_builder import ContextBuilder, ContextExtender
from typing import Dict, Any, Optional, List, Callable, Awaitable

# Type alias for context extenders
ContextExtender = Callable[
    [Dict[str, Any], Optional[Any]],
    Awaitable[Dict[str, Any]]
]

class ContextBuilder:
    """
    Builds resolution context for template processing.

    The context combines environment, configuration, application state,
    and custom extender outputs into a unified dictionary.
    """

    @staticmethod
    async def build(
        options: Dict[str, Any],
        extenders: List[ContextExtender] = None
    ) -> Dict[str, Any]:
        """
        Build resolution context.

        Args:
            options: Dictionary containing:
                - env: Environment variables (defaults to os.environ)
                - config: Raw configuration dictionary
                - app: Application metadata
                - state: Runtime state
                - request: HTTP request object (optional)
            extenders: List of async functions to extend context

        Returns:
            Combined context dictionary

        Example:
            context = await ContextBuilder.build({
                'config': {'app': {'name': 'MyApp'}},
                'app': {'name': 'MyApp', 'version': '1.0.0'},
                'state': {'count': 42}
            }, extenders=[auth_extender])
        """
```

#### Usage

```python
import os

# Define context extenders
async def auth_extender(ctx: Dict[str, Any], request: Any) -> Dict[str, Any]:
    """Extract auth from request headers."""
    auth_header = ''
    if request and hasattr(request, 'headers'):
        auth_header = request.headers.get('authorization', '')

    return {
        'auth': {
            'token': auth_header.replace('Bearer ', '') if auth_header else None,
            'authenticated': bool(auth_header)
        }
    }

async def tenant_extender(ctx: Dict[str, Any], request: Any) -> Dict[str, Any]:
    """Extract tenant from request headers. Can access previous extender results."""
    tenant_id = 'default'
    if request and hasattr(request, 'headers'):
        tenant_id = request.headers.get('x-tenant-id', 'default')

    return {
        'tenant': {
            'id': tenant_id,
            'name': f'Tenant {tenant_id}',
            # Can access auth from previous extender
            'owner': ctx.get('auth', {}).get('user_id')
        }
    }

# Build context
context = await ContextBuilder.build(
    {
        'env': dict(os.environ),
        'config': raw_config,
        'app': {'name': 'MyApp', 'version': '1.0.0'},
        'state': {'request_count': 42},
        'request': fastapi_request
    },
    extenders=[auth_extender, tenant_extender]
)

# Access context values
print(context['env']['HOME'])
print(context['app']['name'])
print(context['auth']['token'])
print(context['tenant']['id'])
```

---

### OverwriteMerger

```python
from app_yaml_overwrites.overwrite_merger import apply_overwrites
from typing import Dict, Any

def apply_overwrites(
    original_config: Dict[str, Any],
    overwrite_section: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deep merge overwrite_section into original_config.

    Args:
        original_config: Base configuration dictionary
        overwrite_section: Overwrites to apply

    Returns:
        New dictionary with overwrites applied (does not mutate original)

    Behavior:
        - If both values are dicts, recursively merge
        - Otherwise, overwrite value replaces original
        - Returns original if overwrite_section is None/empty
    """
```

#### Usage

```python
# Basic merge
original = {
    'database': {
        'host': 'localhost',
        'port': 5432,
        'password': None  # placeholder
    }
}

overwrites = {
    'database': {
        'password': 'secret123'
    }
}

result = apply_overwrites(original, overwrites)
# result['database']['password'] == 'secret123'
# result['database']['host'] == 'localhost' (preserved)

# overwrite_from_context pattern
provider_config = {
    'base_url': 'https://api.example.com',
    'headers': {
        'Authorization': None,
        'X-Tenant-Id': None
    },
    'overwrite_from_context': {
        'headers': {
            'Authorization': 'Bearer resolved-token',
            'X-Tenant-Id': 'tenant-123'
        }
    }
}

resolved = apply_overwrites(
    provider_config,
    provider_config.get('overwrite_from_context', {})
)
```

---

### ConfigSDK

```python
from app_yaml_overwrites import ConfigSDK
from typing import Dict, Any, List, Optional

class ConfigSDK:
    """
    High-level SDK for configuration management.

    Implements singleton pattern for application-wide configuration access.
    Combines static YAML loading with runtime template resolution.
    """

    _instance: Optional['ConfigSDK'] = None

    def __init__(self, options: Dict[str, Any] = None):
        """
        Initialize SDK instance (use initialize() instead).

        Args:
            options: Configuration options
                - context_extenders: List of async extender functions
        """

    @classmethod
    async def initialize(cls, options: Dict[str, Any] = None) -> 'ConfigSDK':
        """
        Async singleton initialization.

        Args:
            options: Configuration options
                - context_extenders: List of context extender functions

        Returns:
            Initialized ConfigSDK instance

        Raises:
            RuntimeError: If AppYamlConfig is not available
        """

    @classmethod
    def get_instance(cls) -> 'ConfigSDK':
        """
        Get existing SDK instance.

        Returns:
            Existing ConfigSDK instance

        Raises:
            RuntimeError: If initialize() hasn't been called
        """

    def get_raw(self) -> Dict[str, Any]:
        """
        Get raw configuration without resolution.

        Returns:
            Raw configuration dictionary
        """

    async def get_resolved(
        self,
        scope: str,
        request: Any = None
    ) -> Dict[str, Any]:
        """
        Get resolved configuration for given scope.

        Args:
            scope: Resolution scope ('STARTUP' or 'REQUEST')
            request: HTTP request for request-scoped resolution

        Returns:
            Resolved configuration dictionary

        Raises:
            RuntimeError: If SDK not initialized
        """

    async def to_json(
        self,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Export configuration as JSON-serializable dictionary.

        Args:
            options: Export options (reserved for future use)

        Returns:
            Configuration dictionary
        """
```

#### Usage

```python
# Initialize (typically during app startup)
sdk = await ConfigSDK.initialize({
    'context_extenders': [auth_extender, tenant_extender]
})

# Get raw config
config = sdk.get_raw()
print(config['app']['name'])

# Get resolved config (with template processing)
resolved = await sdk.get_resolved('REQUEST', request)

# Later: access existing instance
instance = ConfigSDK.get_instance()
```

---

## FastAPI Integration

### Lifespan Pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    sdk = await ConfigSDK.initialize({
        'context_extenders': [auth_extender, tenant_extender]
    })
    app.state.config = sdk.get_raw()
    app.state.sdk = sdk

    yield

    # Shutdown (cleanup if needed)

app = FastAPI(lifespan=lifespan)
```

### Dependency Injection Pattern

```python
from typing import Annotated
from fastapi import Depends, Request

async def get_config() -> Dict[str, Any]:
    return app.state.config

async def get_context(request: Request) -> Dict[str, Any]:
    return await ContextBuilder.build(
        {'config': app.state.config, 'request': request},
        extenders=[auth_extender, tenant_extender]
    )

Config = Annotated[Dict[str, Any], Depends(get_config)]
Context = Annotated[Dict[str, Any], Depends(get_context)]

@app.get('/health')
async def health(config: Config):
    return {'status': 'healthy', 'app': config['app']['name']}

@app.get('/providers/{name}')
async def get_provider(name: str, config: Config, context: Context):
    provider = config['providers'][name]
    resolved = apply_overwrites(provider, resolve_templates(
        provider.get('overwrite_from_context', {}), context
    ))
    return resolved
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `debug` | Log level: `trace`, `debug`, `info`, `warn`, `error` |

---

## Type Hints

The package uses Python type hints throughout:

```python
from typing import Dict, Any, List, Optional, Callable, Awaitable

# Context extender type
ContextExtender = Callable[
    [Dict[str, Any], Optional[Any]],
    Awaitable[Dict[str, Any]]
]
```

---

## See Also

- [SDK Guide](../../docs/SDK_GUIDE.md)
- [Server Integration](../../docs/SERVER_INTEGRATION.md)
- [Examples](../examples/)
