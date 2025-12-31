#!/usr/bin/env python3
"""
Runtime Template Resolver - Basic Usage Examples

This script demonstrates core features of the runtime_template_resolver package:
- Simple placeholder resolution
- Nested path resolution
- Default values
- Missing value strategies
- Object/config resolution
- Template compilation
- Placeholder extraction and validation
"""
import sys
import os

# Add parent src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from runtime_template_resolver import (
    TemplateResolver,
    resolve,
    resolve_many,
    resolve_object,
    validate,
    extract,
    compile,
    MissingStrategy,
    ResolverOptions,
    SecurityError,
    ValidationError,
    MissingValueError,
)


# =============================================================================
# Example 1: Simple Placeholder Resolution
# =============================================================================
def example1_simple_resolution() -> None:
    """
    Demonstrates basic placeholder resolution with simple key-value context.
    """
    print("\n" + "=" * 60)
    print("Example 1: Simple Placeholder Resolution")
    print("=" * 60)

    resolver = TemplateResolver()

    # Simple greeting template
    template = "Hello, {{name}}! Welcome to {{company}}."
    context = {"name": "Alice", "company": "ACME Corp"}

    result = resolver.resolve(template, context)
    print(f"Template: {template}")
    print(f"Context:  {context}")
    print(f"Result:   {result}")


# =============================================================================
# Example 2: Nested Path Resolution
# =============================================================================
def example2_nested_paths() -> None:
    """
    Demonstrates resolution of nested object paths using dot notation.
    """
    print("\n" + "=" * 60)
    print("Example 2: Nested Path Resolution")
    print("=" * 60)

    resolver = TemplateResolver()

    template = "User {{user.profile.name}} ({{user.profile.email}}) has role: {{user.role}}"
    context = {
        "user": {
            "profile": {
                "name": "Bob Smith",
                "email": "bob@example.com"
            },
            "role": "admin"
        }
    }

    result = resolver.resolve(template, context)
    print(f"Template: {template}")
    print(f"Result:   {result}")


# =============================================================================
# Example 3: Array Access
# =============================================================================
def example3_array_access() -> None:
    """
    Demonstrates resolution of array elements using bracket notation.
    """
    print("\n" + "=" * 60)
    print("Example 3: Array Access")
    print("=" * 60)

    resolver = TemplateResolver()

    template = "Top items: {{items[0]}}, {{items[1]}}, {{items[2]}}"
    context = {
        "items": ["Apple", "Banana", "Cherry", "Date"]
    }

    result = resolver.resolve(template, context)
    print(f"Template: {template}")
    print(f"Result:   {result}")


# =============================================================================
# Example 4: Default Values
# =============================================================================
def example4_default_values() -> None:
    """
    Demonstrates using default values for missing placeholders.
    """
    print("\n" + "=" * 60)
    print("Example 4: Default Values")
    print("=" * 60)

    resolver = TemplateResolver()

    # Various default value syntaxes
    templates = [
        ('DB Host: {{db.host | "localhost"}}', {}),
        ("DB Port: {{db.port | '5432'}}", {}),
        ("Environment: {{env | production}}", {}),
        ('API Key: {{api_key | "not-set"}}', {"api_key": "secret-123"}),
    ]

    for template, context in templates:
        result = resolver.resolve(template, context)
        print(f"Template: {template}")
        print(f"Result:   {result}")
        print()


# =============================================================================
# Example 5: Missing Value Strategies
# =============================================================================
def example5_missing_strategies() -> None:
    """
    Demonstrates different strategies for handling missing values.
    """
    print("\n" + "=" * 60)
    print("Example 5: Missing Value Strategies")
    print("=" * 60)

    resolver = TemplateResolver()
    template = "Value: {{missing_key}}"
    context = {}

    strategies = [
        (MissingStrategy.EMPTY, "Replace with empty string"),
        (MissingStrategy.KEEP, "Keep original placeholder"),
        (MissingStrategy.DEFAULT, "Use default value (empty if none)"),
    ]

    for strategy, description in strategies:
        opts = ResolverOptions(missing_strategy=strategy)
        result = resolver.resolve(template, context, options=opts)
        print(f"Strategy {strategy.value}: {description}")
        print(f"  Result: '{result}'")
        print()

    # ERROR strategy throws exception
    print("Strategy ERROR: Throws exception")
    try:
        opts = ResolverOptions(missing_strategy=MissingStrategy.ERROR, throw_on_error=True)
        resolver.resolve(template, context, options=opts)
    except MissingValueError as e:
        print(f"  Caught: {e}")


# =============================================================================
# Example 6: Resolve Object (Config Templates)
# =============================================================================
def example6_resolve_object() -> None:
    """
    Demonstrates resolving templates within nested objects/configs.
    """
    print("\n" + "=" * 60)
    print("Example 6: Resolve Object (Config Templates)")
    print("=" * 60)

    resolver = TemplateResolver()

    # Simulated config object with templates
    config = {
        "database": {
            "url": "postgres://{{db.host}}:{{db.port}}/{{db.name}}",
            "pool_size": 10
        },
        "api": {
            "base_url": "https://{{api.domain}}/v{{api.version}}",
            "endpoints": [
                "/users/{{user_id}}",
                "/orders/{{order_id}}"
            ]
        },
        "messages": {
            "welcome": "Welcome {{user.name}} to {{app.name}}!"
        }
    }

    context = {
        "db": {"host": "localhost", "port": "5432", "name": "myapp"},
        "api": {"domain": "api.example.com", "version": "2"},
        "user_id": "123",
        "order_id": "456",
        "user": {"name": "Alice"},
        "app": {"name": "MyApp"}
    }

    resolved = resolver.resolve_object(config, context)

    print("Original config with templates:")
    print(f"  database.url: {config['database']['url']}")
    print(f"  api.base_url: {config['api']['base_url']}")
    print()
    print("Resolved config:")
    print(f"  database.url: {resolved['database']['url']}")
    print(f"  api.base_url: {resolved['api']['base_url']}")
    print(f"  api.endpoints: {resolved['api']['endpoints']}")
    print(f"  messages.welcome: {resolved['messages']['welcome']}")


# =============================================================================
# Example 7: Template Compilation
# =============================================================================
def example7_compilation() -> None:
    """
    Demonstrates compiling templates for repeated use.
    """
    print("\n" + "=" * 60)
    print("Example 7: Template Compilation")
    print("=" * 60)

    # Compile template once
    email_template = compile(
        "Dear {{name}},\n\n"
        "Your order #{{order_id}} has been {{status}}.\n\n"
        "Best regards,\n{{company}}"
    )

    # Use multiple times with different contexts
    orders = [
        {"name": "Alice", "order_id": "1001", "status": "shipped", "company": "ACME"},
        {"name": "Bob", "order_id": "1002", "status": "delivered", "company": "ACME"},
        {"name": "Charlie", "order_id": "1003", "status": "processing", "company": "ACME"},
    ]

    for order in orders:
        result = email_template(order)
        print(f"--- Order #{order['order_id']} ---")
        print(result)
        print()


# =============================================================================
# Example 8: Placeholder Extraction
# =============================================================================
def example8_extraction() -> None:
    """
    Demonstrates extracting placeholder keys from templates.
    """
    print("\n" + "=" * 60)
    print("Example 8: Placeholder Extraction")
    print("=" * 60)

    templates = [
        "Hello {{name}}!",
        "{{user.profile.name}} works at {{company}}",
        "Items: {{items[0]}}, {{items[1]}}",
        '{{value | "default"}}',
    ]

    for template in templates:
        placeholders = extract(template)
        print(f"Template: {template}")
        print(f"  Placeholders: {placeholders}")
        print()


# =============================================================================
# Example 9: Validation
# =============================================================================
def example9_validation() -> None:
    """
    Demonstrates template validation before resolution.
    """
    print("\n" + "=" * 60)
    print("Example 9: Validation")
    print("=" * 60)

    valid_templates = [
        "{{name}}",
        "{{user.profile.name}}",
        "{{items[0]}}",
        '{{value | "default"}}',
    ]

    invalid_templates = [
        "{{foo@bar}}",  # Invalid character @
        "{{foo..bar}}",  # Empty segment
    ]

    print("Valid templates:")
    for template in valid_templates:
        try:
            validate(template)
            print(f"  {template}")
        except ValidationError as e:
            print(f"  {template} - ERROR: {e}")

    print("\nInvalid templates:")
    for template in invalid_templates:
        try:
            validate(template)
            print(f"  {template} - OK (unexpected)")
        except ValidationError as e:
            print(f"  {template}")
            print(f"    Error: {e}")


# =============================================================================
# Example 10: Security - Private Attribute Protection
# =============================================================================
def example10_security() -> None:
    """
    Demonstrates security protection against private attribute access.
    """
    print("\n" + "=" * 60)
    print("Example 10: Security - Private Attribute Protection")
    print("=" * 60)

    resolver = TemplateResolver()

    dangerous_templates = [
        "{{_private}}",
        "{{__class__}}",
        "{{obj.__dict__}}",
    ]

    print("Attempting to access private attributes:")
    for template in dangerous_templates:
        try:
            opts = ResolverOptions(throw_on_error=True)
            result = resolver.resolve(template, {"_private": "secret"}, options=opts)
            print(f"  {template} -> {result}")
        except SecurityError as e:
            print(f"  {template}")
            print(f"    Blocked: {e}")


# =============================================================================
# Example 11: SDK Convenience Functions
# =============================================================================
def example11_sdk_functions() -> None:
    """
    Demonstrates using SDK-level convenience functions.
    """
    print("\n" + "=" * 60)
    print("Example 11: SDK Convenience Functions")
    print("=" * 60)

    context = {"name": "World", "count": 42}

    # resolve() - single template
    result = resolve("Hello {{name}}!", context)
    print(f"resolve(): {result}")

    # resolve_many() - multiple templates
    results = resolve_many([
        "Hello {{name}}",
        "Count: {{count}}",
        "Goodbye {{name}}"
    ], context)
    print(f"resolve_many(): {results}")

    # resolve_object() - nested objects
    obj = {"greeting": "Hello {{name}}", "data": {"value": "{{count}}"}}
    resolved = resolve_object(obj, context)
    print(f"resolve_object(): {resolved}")


# =============================================================================
# Main Runner
# =============================================================================
def main() -> None:
    """Run all examples sequentially."""
    print("=" * 60)
    print("Runtime Template Resolver - Basic Usage Examples")
    print("=" * 60)

    example1_simple_resolution()
    example2_nested_paths()
    example3_array_access()
    example4_default_values()
    example5_missing_strategies()
    example6_resolve_object()
    example7_compilation()
    example8_extraction()
    example9_validation()
    example10_security()
    example11_sdk_functions()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
