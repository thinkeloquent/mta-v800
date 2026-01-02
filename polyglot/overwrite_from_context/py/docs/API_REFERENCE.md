# Runtime Template Resolver - Python API Reference

Complete Python API reference for the `runtime_template_resolver` package.

## Installation

```bash
pip install runtime-template-resolver
# or with poetry
poetry add runtime-template-resolver
```

## Module Exports

```python
from runtime_template_resolver import (
    # SDK Factory Functions
    create_registry,
    create_resolver,

    # Core Classes
    ComputeRegistry,
    ContextResolver,
    Security,

    # Configuration
    ComputeScope,
    MissingStrategy,
    ResolverOptions,

    # Logging
    Logger,
    LogLevel,
    ILogger,

    # Errors
    ErrorCode,
    ResolveError,
    ComputeFunctionError,
    SecurityError,
    RecursionLimitError,
    ScopeViolationError,
    ValidationError,

    # Types
    types
)
```

## SDK Factory Functions

### create_registry

```python
def create_registry(logger: Optional[Logger] = None) -> ComputeRegistry:
    """
    Factory function to create a new ComputeRegistry.

    Args:
        logger: Optional logger instance for debug output

    Returns:
        ComputeRegistry: New registry instance
    """
```

### create_resolver

```python
def create_resolver(
    registry: Optional[ComputeRegistry] = None,
    options: Optional[ResolverOptions] = None,
    logger: Optional[Logger] = None
) -> ContextResolver:
    """
    Factory function to create a new ContextResolver.

    Args:
        registry: Optional compute registry (created if not provided)
        options: Optional resolver configuration
        logger: Optional logger instance

    Returns:
        ContextResolver: New resolver instance
    """
```

## Core Classes

### ComputeRegistry

```python
class ComputeRegistry:
    """Registry for compute functions invoked via {{fn:name}} patterns."""

    def __init__(self, logger: Optional[Logger] = None) -> None: ...

    def register(self, name: str, fn: Callable, scope: ComputeScope) -> None:
        """
        Register a compute function.

        Args:
            name: Function name (must match ^[a-zA-Z_][a-zA-Z0-9_]*$)
            fn: Callable that optionally accepts context dict
            scope: ComputeScope.STARTUP or ComputeScope.REQUEST

        Raises:
            ValueError: If name is empty or invalid
        """

    def unregister(self, name: str) -> None:
        """Remove a registered function."""

    def has(self, name: str) -> bool:
        """Check if function is registered."""

    def list(self) -> List[str]:
        """Get list of registered function names."""

    def get_scope(self, name: str) -> Optional[ComputeScope]:
        """Get scope of registered function."""

    def clear(self) -> None:
        """Clear all registered functions and cache."""

    def clear_cache(self) -> None:
        """Clear cached STARTUP results only."""

    async def resolve(
        self,
        name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute a registered function.

        Args:
            name: Function name
            context: Optional context dict passed to function

        Returns:
            Function result (cached for STARTUP scope)

        Raises:
            ComputeFunctionError: If function not found or execution fails
        """
```

### ContextResolver

```python
class ContextResolver:
    """Main resolver for template and compute patterns."""

    def __init__(
        self,
        registry: ComputeRegistry,
        options: Optional[ResolverOptions] = None
    ) -> None: ...

    def is_compute_pattern(self, expression: str) -> bool:
        """Check if expression is a compute pattern ({{fn:...}})."""

    async def resolve(
        self,
        expression: Any,
        context: Dict[str, Any],
        scope: ComputeScope = ComputeScope.REQUEST,
        depth: int = 0
    ) -> Any:
        """
        Resolve a single expression.

        Args:
            expression: Pattern string or pass-through value
            context: Context dict for variable lookup
            scope: Resolution scope (STARTUP or REQUEST)
            depth: Current recursion depth (internal)

        Returns:
            Resolved value with type inference

        Raises:
            RecursionLimitError: If max_depth exceeded
            ScopeViolationError: If REQUEST function called in STARTUP
            ComputeFunctionError: If compute function fails
            SecurityError: If path validation fails
        """

    async def resolve_object(
        self,
        obj: Any,
        context: Dict[str, Any],
        scope: ComputeScope = ComputeScope.REQUEST,
        depth: int = 0
    ) -> Any:
        """
        Recursively resolve all patterns in nested object.

        Args:
            obj: Dict, list, or scalar value
            context: Context dict for variable lookup
            scope: Resolution scope
            depth: Current recursion depth

        Returns:
            Deep copy with all patterns resolved
        """

    async def resolve_many(
        self,
        expressions: List[Any],
        context: Dict[str, Any],
        scope: ComputeScope = ComputeScope.REQUEST
    ) -> List[Any]:
        """Resolve multiple expressions."""
```

### Security

```python
class Security:
    """Static utility for path validation."""

    PATH_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_.]*$')

    BLOCKED_PATTERNS = {
        "__proto__", "__class__", "__dict__",
        "constructor", "prototype"
    }

    @classmethod
    def validate_path(cls, path: str) -> None:
        """
        Validate context path for security.

        Args:
            path: Dot-notation path string

        Raises:
            SecurityError: If path is blocked or invalid
        """
```

## Configuration

### ComputeScope

```python
class ComputeScope(Enum):
    STARTUP = "STARTUP"   # Cached at startup
    REQUEST = "REQUEST"   # Executed per-request
```

### MissingStrategy

```python
class MissingStrategy(Enum):
    ERROR = "ERROR"       # Raise error on missing
    DEFAULT = "DEFAULT"   # Return None
    IGNORE = "IGNORE"     # Return original pattern
```

### ResolverOptions

```python
@dataclass
class ResolverOptions:
    max_depth: int = 10
    missing_strategy: MissingStrategy = MissingStrategy.ERROR
    logger: Optional[Logger] = None
```

## Errors

### Error Hierarchy

```python
class ResolveError(Exception):
    """Base class for all resolver errors."""
    code: str
    context: dict

class ComputeFunctionError(ResolveError): ...
class SecurityError(ResolveError): ...
class RecursionLimitError(ResolveError): ...
class ScopeViolationError(ResolveError): ...
class ValidationError(ResolveError): ...
```

### ErrorCode

```python
class ErrorCode:
    COMPUTE_FUNCTION_NOT_FOUND = "ERR_COMPUTE_NOT_FOUND"
    COMPUTE_FUNCTION_FAILED = "ERR_COMPUTE_FAILED"
    SECURITY_BLOCKED_PATH = "ERR_SECURITY_PATH"
    RECURSION_LIMIT = "ERR_RECURSION_LIMIT"
    SCOPE_VIOLATION = "ERR_SCOPE_VIOLATION"
    VALIDATION_ERROR = "ERR_VALIDATION_ERROR"
```

## FastAPI Integration

```python
from runtime_template_resolver.integrations.fastapi import (
    resolve_startup,
    get_request_config
)
```

### resolve_startup

```python
async def resolve_startup(
    app: FastAPI,
    config: Dict[str, Any],
    registry: ComputeRegistry,
    state_property: str = "config",
    logger: Optional[Logger] = None
) -> None:
    """
    Resolve configuration at STARTUP scope and store in app.state.

    Args:
        app: FastAPI application instance
        config: Raw configuration dict with patterns
        registry: ComputeRegistry with registered functions
        state_property: Property name on app.state (supports dot notation)
        logger: Optional logger

    Side Effects:
        - Sets app.state.{state_property} to resolved config
        - Sets app.state._context_resolver
        - Sets app.state._context_registry
        - Sets app.state._context_raw_config
    """
```

### get_request_config

```python
async def get_request_config(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency for REQUEST-scope configuration.

    Args:
        request: FastAPI Request object

    Returns:
        Fully resolved configuration dict

    Raises:
        RuntimeError: If resolve_startup was not called
    """
```

## Usage Examples

### Basic Resolution

```python
import asyncio
from runtime_template_resolver import (
    create_registry, create_resolver, ComputeScope
)

async def main():
    registry = create_registry()
    resolver = create_resolver(registry)

    # Register functions
    registry.register("get_version", lambda: "1.0.0", ComputeScope.STARTUP)

    # Resolve patterns
    context = {"env": {"APP_NAME": "MyApp"}}

    name = await resolver.resolve("{{env.APP_NAME}}", context)
    version = await resolver.resolve("{{fn:get_version}}", context)
    missing = await resolver.resolve("{{env.MISSING | 'default'}}", context)

    print(f"Name: {name}, Version: {version}, Missing: {missing}")

asyncio.run(main())
```

### FastAPI Integration

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from typing import Annotated, Dict, Any

from runtime_template_resolver import create_registry, ComputeScope
from runtime_template_resolver.integrations.fastapi import (
    resolve_startup, get_request_config
)

registry = create_registry()
registry.register("get_version", lambda: "1.0.0", ComputeScope.STARTUP)

config = {
    "app": {"name": "{{env.APP_NAME | 'MyApp'}}", "version": "{{fn:get_version}}"}
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    await resolve_startup(app, config, registry)
    yield

app = FastAPI(lifespan=lifespan)

ResolvedConfig = Annotated[Dict[str, Any], Depends(get_request_config)]

@app.get("/config")
async def get_config(config: ResolvedConfig):
    return config
```
