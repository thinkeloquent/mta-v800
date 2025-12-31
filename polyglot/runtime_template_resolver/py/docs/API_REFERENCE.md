# Runtime Template Resolver - Python API Reference

Complete API reference for the Python implementation of the runtime template resolver.

## Core Components

### TemplateResolver

The main class for resolving templates with placeholder substitution.

```python
from runtime_template_resolver import TemplateResolver, ResolverOptions

class TemplateResolver:
    def __init__(self) -> None: ...

    def resolve(
        self,
        template: str,
        context: Dict[str, Any],
        options: Optional[ResolverOptions] = None
    ) -> str: ...

    def resolve_object(
        self,
        obj: Any,
        context: Dict[str, Any],
        options: Optional[ResolverOptions] = None
    ) -> Any: ...
```

### ResolverOptions

Configuration options for template resolution.

```python
from runtime_template_resolver import ResolverOptions, MissingStrategy

@dataclass
class ResolverOptions:
    missing_strategy: MissingStrategy = MissingStrategy.EMPTY
    throw_on_error: bool = False
```

### MissingStrategy

Enum defining how to handle missing placeholder values.

```python
from runtime_template_resolver import MissingStrategy

class MissingStrategy(Enum):
    EMPTY = "empty"      # Replace with empty string
    KEEP = "keep"        # Keep original placeholder
    ERROR = "error"      # Raise MissingValueError
    DEFAULT = "default"  # Use default value if provided
```

## SDK Functions

High-level convenience functions for common operations.

```python
from runtime_template_resolver import (
    resolve,
    resolve_many,
    resolve_object,
    validate,
    extract,
    compile,
    validate_placeholder,
    extract_placeholders,
)
```

### resolve

Resolve a single template string.

```python
def resolve(
    template: str,
    context: Dict[str, Any],
    options: Optional[ResolverOptions] = None
) -> str: ...

# Example
result = resolve("Hello {{name}}!", {"name": "World"})
# Returns: "Hello World!"
```

### resolve_many

Resolve multiple templates with the same context.

```python
def resolve_many(
    templates: List[str],
    context: Dict[str, Any],
    options: Optional[ResolverOptions] = None
) -> List[str]: ...

# Example
results = resolve_many(
    ["Hello {{name}}", "Count: {{count}}"],
    {"name": "World", "count": 42}
)
# Returns: ["Hello World", "Count: 42"]
```

### resolve_object

Recursively resolve templates within nested objects.

```python
def resolve_object(
    obj: Any,
    context: Dict[str, Any],
    options: Optional[ResolverOptions] = None
) -> Any: ...

# Example
config = {"url": "https://{{host}}/api"}
resolved = resolve_object(config, {"host": "example.com"})
# Returns: {"url": "https://example.com/api"}
```

### validate

Validate a template string for syntax errors.

```python
def validate(template: str) -> None: ...

# Example
validate("{{user.name}}")  # OK
validate("{{foo@bar}}")    # Raises ValidationError
```

### extract

Extract placeholder keys from a template.

```python
def extract(template: str) -> List[str]: ...

# Example
keys = extract("{{user.name}} at {{company}}")
# Returns: ["user.name", "company"]
```

### compile

Pre-compile a template for repeated use.

```python
def compile(template: str) -> Callable[[Dict[str, Any]], str]: ...

# Example
email_template = compile("Dear {{name}}, ...")
result1 = email_template({"name": "Alice"})
result2 = email_template({"name": "Bob"})
```

### validate_placeholder

Validate a single placeholder key.

```python
def validate_placeholder(placeholder: str) -> None: ...

# Example
validate_placeholder("user.profile.name")  # OK
validate_placeholder("_private")           # Raises ValidationError
```

### extract_placeholders

Extract and trim placeholders from a template.

```python
def extract_placeholders(template: str) -> List[str]: ...

# Example
placeholders = extract_placeholders("{{  name  }}")
# Returns: ["name"]
```

## Exceptions

### SecurityError

Raised when accessing private or unsafe attributes.

```python
from runtime_template_resolver import SecurityError

class SecurityError(Exception):
    """Raised when access to private/unsafe attribute is denied."""
    pass
```

### ValidationError

Raised when template syntax is invalid.

```python
from runtime_template_resolver import ValidationError

class ValidationError(Exception):
    """Raised when template or placeholder validation fails."""
    pass
```

### MissingValueError

Raised when a required placeholder value is missing (with ERROR strategy).

```python
from runtime_template_resolver import MissingValueError

class MissingValueError(Exception):
    """Raised when a placeholder value is missing."""
    pass
```

## FastAPI Integration

### create_resolver_dependency

Create a FastAPI dependency for template resolution.

```python
from runtime_template_resolver.integrations.fastapi_utils import (
    create_resolver_dependency,
    ConfiguredResolverProtocol,
)

def create_resolver_dependency(
    options: Optional[ResolverOptions] = None
) -> Callable[[], ConfiguredResolverProtocol]: ...

# Usage in FastAPI
get_resolver = create_resolver_dependency()

@app.get("/resolve")
def endpoint(resolver: ConfiguredResolverProtocol = Depends(get_resolver)):
    return resolver.resolve("{{name}}", {"name": "World"})
```

### ConfiguredResolverProtocol

Protocol for the configured resolver instance.

```python
class ConfiguredResolverProtocol(Protocol):
    def resolve(
        self,
        template: str,
        context: Dict[str, Any],
        options: Optional[ResolverOptions] = None
    ) -> str: ...

    def resolve_object(
        self,
        obj: Any,
        context: Dict[str, Any],
        options: Optional[ResolverOptions] = None
    ) -> Any: ...
```
