# Runtime Template Resolver - Python SDK Guide

The Runtime Template Resolver SDK provides a high-level API for resolving template strings with dynamic placeholders. It's designed for CLI tools, LLM Agents, and configuration management systems.

## Installation

```bash
# Using poetry
poetry add runtime-template-resolver

# Using pip
pip install runtime-template-resolver
```

## Quick Start

```python
from runtime_template_resolver import resolve, resolve_object

# Simple resolution
message = resolve("Hello {{name}}!", {"name": "World"})
print(message)  # Hello World!

# Resolve configuration objects
config = {
    "database": {
        "url": "postgres://{{db.host}}:{{db.port}}/{{db.name}}"
    }
}
context = {"db": {"host": "localhost", "port": "5432", "name": "myapp"}}
resolved = resolve_object(config, context)
print(resolved["database"]["url"])  # postgres://localhost:5432/myapp
```

## Usage

### Basic Template Resolution

```python
from runtime_template_resolver import TemplateResolver

resolver = TemplateResolver()

# Simple placeholder
result = resolver.resolve("Hello {{name}}!", {"name": "Alice"})

# Nested paths
result = resolver.resolve(
    "User: {{user.profile.name}}",
    {"user": {"profile": {"name": "Alice"}}}
)

# Array access
result = resolver.resolve(
    "First item: {{items[0]}}",
    {"items": ["apple", "banana", "cherry"]}
)
```

### Default Values

```python
from runtime_template_resolver import resolve

# Double quotes
result = resolve('Host: {{host | "localhost"}}', {})
# Returns: "Host: localhost"

# Single quotes
result = resolve("Port: {{port | '5432'}}", {})
# Returns: "Port: 5432"

# No quotes
result = resolve("Env: {{env | production}}", {})
# Returns: "Env: production"
```

### Missing Value Strategies

```python
from runtime_template_resolver import (
    TemplateResolver,
    ResolverOptions,
    MissingStrategy,
)

resolver = TemplateResolver()
template = "Value: {{missing}}"

# EMPTY - Replace with empty string (default)
opts = ResolverOptions(missing_strategy=MissingStrategy.EMPTY)
result = resolver.resolve(template, {}, options=opts)
# Returns: "Value: "

# KEEP - Keep original placeholder
opts = ResolverOptions(missing_strategy=MissingStrategy.KEEP)
result = resolver.resolve(template, {}, options=opts)
# Returns: "Value: {{missing}}"

# ERROR - Raise exception
opts = ResolverOptions(
    missing_strategy=MissingStrategy.ERROR,
    throw_on_error=True
)
try:
    resolver.resolve(template, {}, options=opts)
except MissingValueError as e:
    print(f"Error: {e}")
```

### Template Compilation

For templates used repeatedly, compile them for better performance:

```python
from runtime_template_resolver import compile

# Compile once
email_template = compile("""
Dear {{name}},

Your order #{{order_id}} has been {{status}}.

Best regards,
{{company}}
""")

# Use multiple times
for order in orders:
    email = email_template({
        "name": order.customer_name,
        "order_id": order.id,
        "status": order.status,
        "company": "ACME Corp"
    })
    send_email(email)
```

### Validation

```python
from runtime_template_resolver import validate, validate_placeholder, ValidationError

# Validate entire template
try:
    validate("{{user.name}}")  # OK
    validate("{{foo@bar}}")    # Raises ValidationError
except ValidationError as e:
    print(f"Invalid template: {e}")

# Validate single placeholder
try:
    validate_placeholder("user.profile.name")  # OK
    validate_placeholder("_private")           # Raises ValidationError
except ValidationError as e:
    print(f"Invalid placeholder: {e}")
```

### Extracting Placeholders

```python
from runtime_template_resolver import extract, extract_placeholders

# Extract placeholder keys
keys = extract("Hello {{name}}, you have {{count}} messages")
print(keys)  # ["name", "count"]

# Extract with whitespace handling
keys = extract_placeholders("{{  name  }}")
print(keys)  # ["name"]
```

## Features

### Core Operations

- `resolve(template, context)` - Resolve single template
- `resolve_many(templates, context)` - Resolve multiple templates
- `resolve_object(obj, context)` - Resolve templates in nested objects

### Validation Operations

- `validate(template)` - Validate template syntax
- `validate_placeholder(placeholder)` - Validate single placeholder

### Utility Operations

- `extract(template)` - Extract placeholder keys
- `extract_placeholders(template)` - Extract and trim placeholders
- `compile(template)` - Pre-compile template for reuse

### Security Features

- Private attribute protection (`_private`, `__dunder__`)
- Path traversal prevention
- Input validation

## Error Handling

```python
from runtime_template_resolver import (
    SecurityError,
    ValidationError,
    MissingValueError,
)

try:
    result = resolve("{{_private}}", {"_private": "secret"})
except SecurityError as e:
    print(f"Security violation: {e}")
except ValidationError as e:
    print(f"Invalid template: {e}")
except MissingValueError as e:
    print(f"Missing value: {e}")
```
