#!/usr/bin/env python3
"""
Runtime Template Resolver - Basic Usage Examples

This script demonstrates the core features of the runtime_template_resolver package:
- Template pattern resolution ({{variable.path}})
- Compute pattern resolution ({{fn:function_name}})
- Default value handling
- Scope enforcement (STARTUP vs REQUEST)
- Object resolution for nested configurations

Run with: python basic_usage.py
"""
import asyncio
import os
from typing import Dict, Any

from runtime_template_resolver import (
    ComputeScope,
    create_registry,
    create_resolver
)


# =============================================================================
# Example 1: Basic Template Resolution
# =============================================================================
async def example1_template_resolution() -> None:
    """
    Demonstrates basic template pattern resolution.

    Template patterns use the format {{path.to.value}} to extract values
    from a context dictionary. Default values can be specified with | operator.
    """
    print("\n" + "=" * 60)
    print("Example 1: Basic Template Resolution")
    print("=" * 60)

    # Create resolver
    registry = create_registry()
    resolver = create_resolver(registry=registry)

    # Context data (simulating environment and config)
    context = {
        "env": {
            "APP_NAME": "MyApplication",
            "DEBUG": "true"
        },
        "config": {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
    }

    # Resolve template patterns
    app_name = await resolver.resolve("{{env.APP_NAME}}", context)
    db_host = await resolver.resolve("{{config.database.host}}", context)

    # Resolve with default values (for missing keys)
    timeout = await resolver.resolve("{{config.timeout | '30'}}", context)
    missing = await resolver.resolve("{{env.MISSING_VAR | 'default_value'}}", context)

    print(f"App Name: {app_name}")
    print(f"DB Host: {db_host}")
    print(f"Timeout (default): {timeout} (type: {type(timeout).__name__})")
    print(f"Missing var (default): {missing}")


# =============================================================================
# Example 2: Compute Function Resolution
# =============================================================================
async def example2_compute_functions() -> None:
    """
    Demonstrates compute function registration and resolution.

    Compute patterns use the format {{fn:function_name}} to call registered
    functions. Functions can access context and return computed values.
    """
    print("\n" + "=" * 60)
    print("Example 2: Compute Function Resolution")
    print("=" * 60)

    registry = create_registry()
    resolver = create_resolver(registry=registry)

    # Register compute functions
    registry.register(
        "get_build_version",
        lambda ctx: "v2.1.0-build.1234",
        ComputeScope.STARTUP
    )

    registry.register(
        "get_connection_string",
        lambda ctx: f"postgresql://{ctx['env'].get('DB_HOST', 'localhost')}:5432/app",
        ComputeScope.STARTUP
    )

    # Simulate request-specific function
    request_counter = {"value": 0}

    def get_request_id(ctx):
        request_counter["value"] += 1
        return f"req-{request_counter['value']:05d}"

    registry.register("get_request_id", get_request_id, ComputeScope.REQUEST)

    # Context with environment
    context = {"env": {"DB_HOST": "db.example.com"}}

    # Resolve compute patterns
    version = await resolver.resolve("{{fn:get_build_version}}", context)
    conn_str = await resolver.resolve("{{fn:get_connection_string}}", context)

    # REQUEST scope functions called multiple times get different results
    req_id1 = await resolver.resolve("{{fn:get_request_id}}", context)
    req_id2 = await resolver.resolve("{{fn:get_request_id}}", context)

    print(f"Build Version: {version}")
    print(f"Connection String: {conn_str}")
    print(f"Request ID (call 1): {req_id1}")
    print(f"Request ID (call 2): {req_id2}")


# =============================================================================
# Example 3: Object Resolution
# =============================================================================
async def example3_object_resolution() -> None:
    """
    Demonstrates resolving entire configuration objects.

    The resolve_object method recursively resolves all template and compute
    patterns within nested dictionaries and lists.
    """
    print("\n" + "=" * 60)
    print("Example 3: Object Resolution")
    print("=" * 60)

    registry = create_registry()
    resolver = create_resolver(registry=registry)

    # Register a compute function
    registry.register(
        "get_timestamp",
        lambda ctx: "2024-01-15T10:30:00Z",
        ComputeScope.STARTUP
    )

    # Configuration template with mixed patterns
    config_template = {
        "app": {
            "name": "{{env.APP_NAME | 'DefaultApp'}}",
            "version": "{{env.APP_VERSION | '1.0.0'}}",
            "debug": "{{env.DEBUG | 'false'}}"
        },
        "database": {
            "host": "{{env.DB_HOST | 'localhost'}}",
            "port": "{{env.DB_PORT | '5432'}}",
            "pool_size": 10  # Non-template values are preserved
        },
        "metadata": {
            "build_time": "{{fn:get_timestamp}}",
            "features": ["auth", "logging", "metrics"]  # Lists preserved
        }
    }

    # Context
    context = {
        "env": {
            "APP_NAME": "ProductionApp",
            "DB_HOST": "db.prod.example.com"
        }
    }

    # Resolve entire object
    resolved_config = await resolver.resolve_object(config_template, context)

    print("Resolved Configuration:")
    print(f"  App Name: {resolved_config['app']['name']}")
    print(f"  App Version: {resolved_config['app']['version']}")
    print(f"  Debug: {resolved_config['app']['debug']} (type: {type(resolved_config['app']['debug']).__name__})")
    print(f"  DB Host: {resolved_config['database']['host']}")
    print(f"  DB Port: {resolved_config['database']['port']} (type: {type(resolved_config['database']['port']).__name__})")
    print(f"  Pool Size: {resolved_config['database']['pool_size']}")
    print(f"  Build Time: {resolved_config['metadata']['build_time']}")
    print(f"  Features: {resolved_config['metadata']['features']}")


# =============================================================================
# Example 4: Scope Enforcement
# =============================================================================
async def example4_scope_enforcement() -> None:
    """
    Demonstrates STARTUP vs REQUEST scope enforcement.

    STARTUP scope functions:
    - Run once at application startup
    - Results are cached
    - Cannot be called at REQUEST scope resolution time when scope is STARTUP

    REQUEST scope functions:
    - Run on each request
    - Results are NOT cached
    - Can be called at both STARTUP and REQUEST scope resolution time
    """
    print("\n" + "=" * 60)
    print("Example 4: Scope Enforcement")
    print("=" * 60)

    registry = create_registry()
    resolver = create_resolver(registry=registry)

    # Track calls to demonstrate caching
    startup_calls = {"count": 0}
    request_calls = {"count": 0}

    def startup_function(ctx=None):
        startup_calls["count"] += 1
        return f"startup-result-{startup_calls['count']}"

    def request_function(ctx):
        request_calls["count"] += 1
        return f"request-result-{request_calls['count']}"

    registry.register("startup_fn", startup_function, ComputeScope.STARTUP)
    registry.register("request_fn", request_function, ComputeScope.REQUEST)

    context = {"env": {}}

    # STARTUP functions are cached
    print("STARTUP scope function (cached):")
    result1 = await resolver.resolve("{{fn:startup_fn}}", context, scope=ComputeScope.REQUEST)
    result2 = await resolver.resolve("{{fn:startup_fn}}", context, scope=ComputeScope.REQUEST)
    result3 = await resolver.resolve("{{fn:startup_fn}}", context, scope=ComputeScope.REQUEST)
    print(f"  Call 1: {result1}")
    print(f"  Call 2: {result2}")
    print(f"  Call 3: {result3}")
    print(f"  Total function executions: {startup_calls['count']}")

    # REQUEST functions are called each time
    print("\nREQUEST scope function (not cached):")
    result1 = await resolver.resolve("{{fn:request_fn}}", context, scope=ComputeScope.REQUEST)
    result2 = await resolver.resolve("{{fn:request_fn}}", context, scope=ComputeScope.REQUEST)
    result3 = await resolver.resolve("{{fn:request_fn}}", context, scope=ComputeScope.REQUEST)
    print(f"  Call 1: {result1}")
    print(f"  Call 2: {result2}")
    print(f"  Call 3: {result3}")
    print(f"  Total function executions: {request_calls['count']}")


# =============================================================================
# Example 5: Default Value Type Inference
# =============================================================================
async def example5_default_type_inference() -> None:
    """
    Demonstrates automatic type inference for default values.

    Default values in patterns are automatically parsed:
    - 'true'/'false' -> boolean
    - Numeric strings -> int or float
    - Other strings -> string
    """
    print("\n" + "=" * 60)
    print("Example 5: Default Value Type Inference")
    print("=" * 60)

    registry = create_registry()
    resolver = create_resolver(registry=registry)

    context = {}  # Empty context to trigger defaults

    # Different default value types
    bool_true = await resolver.resolve("{{missing | 'true'}}", context)
    bool_false = await resolver.resolve("{{missing | 'false'}}", context)
    integer = await resolver.resolve("{{missing | '42'}}", context)
    float_val = await resolver.resolve("{{missing | '3.14'}}", context)
    string_val = await resolver.resolve("{{missing | 'hello'}}", context)

    print("Type inference for defaults:")
    print(f"  'true' -> {bool_true} (type: {type(bool_true).__name__})")
    print(f"  'false' -> {bool_false} (type: {type(bool_false).__name__})")
    print(f"  '42' -> {integer} (type: {type(integer).__name__})")
    print(f"  '3.14' -> {float_val} (type: {type(float_val).__name__})")
    print(f"  'hello' -> {string_val} (type: {type(string_val).__name__})")


# =============================================================================
# Example 6: Realistic Configuration Scenario
# =============================================================================
async def example6_realistic_scenario() -> None:
    """
    Demonstrates a realistic configuration resolution scenario.

    This example shows how the resolver would be used in a real application
    to resolve configuration from environment variables and computed values.
    """
    print("\n" + "=" * 60)
    print("Example 6: Realistic Configuration Scenario")
    print("=" * 60)

    registry = create_registry()
    resolver = create_resolver(registry=registry)

    # Register compute functions
    def build_database_url(ctx):
        env = ctx.get("env", {})
        host = env.get("DB_HOST", "localhost")
        port = env.get("DB_PORT", "5432")
        user = env.get("DB_USER", "app")
        password = env.get("DB_PASSWORD", "secret")
        name = env.get("DB_NAME", "app_db")
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

    def get_log_config(ctx):
        env = ctx.get("env", {})
        level = env.get("LOG_LEVEL", "INFO")
        return {"level": level, "format": "json", "output": "stdout"}

    registry.register("build_database_url", build_database_url, ComputeScope.STARTUP)
    registry.register("get_log_config", get_log_config, ComputeScope.STARTUP)

    # Simulated app.yaml configuration
    app_config = {
        "server": {
            "host": "{{env.HOST | '0.0.0.0'}}",
            "port": "{{env.PORT | '8080'}}",
            "workers": "{{env.WORKERS | '4'}}"
        },
        "database": {
            "url": "{{fn:build_database_url}}",
            "pool_size": "{{env.DB_POOL_SIZE | '10'}}",
            "timeout": "{{env.DB_TIMEOUT | '30'}}"
        },
        "logging": "{{fn:get_log_config}}",
        "features": {
            "auth_enabled": "{{env.AUTH_ENABLED | 'true'}}",
            "rate_limiting": "{{env.RATE_LIMIT | 'false'}}",
            "metrics": "{{env.METRICS_ENABLED | 'true'}}"
        }
    }

    # Set up environment (simulating production)
    original_env = dict(os.environ)
    os.environ.update({
        "DB_HOST": "db.prod.example.com",
        "DB_USER": "app_user",
        "DB_PASSWORD": "super_secret",
        "DB_NAME": "production_db",
        "LOG_LEVEL": "WARNING",
        "PORT": "3000",
        "WORKERS": "8"
    })

    try:
        context = {"env": dict(os.environ)}
        resolved = await resolver.resolve_object(
            app_config,
            context,
            scope=ComputeScope.STARTUP
        )

        print("Resolved Production Configuration:")
        print(f"\nServer:")
        print(f"  Host: {resolved['server']['host']}")
        print(f"  Port: {resolved['server']['port']} (type: {type(resolved['server']['port']).__name__})")
        print(f"  Workers: {resolved['server']['workers']}")

        print(f"\nDatabase:")
        print(f"  URL: {resolved['database']['url']}")
        print(f"  Pool Size: {resolved['database']['pool_size']}")
        print(f"  Timeout: {resolved['database']['timeout']}")

        print(f"\nLogging:")
        print(f"  Config: {resolved['logging']}")

        print(f"\nFeatures:")
        print(f"  Auth Enabled: {resolved['features']['auth_enabled']}")
        print(f"  Rate Limiting: {resolved['features']['rate_limiting']}")
        print(f"  Metrics: {resolved['features']['metrics']}")

    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


# =============================================================================
# Main Runner
# =============================================================================
async def main() -> None:
    """Run all examples sequentially."""
    print("=" * 60)
    print("Runtime Template Resolver - Basic Usage Examples")
    print("=" * 60)

    await example1_template_resolution()
    await example2_compute_functions()
    await example3_object_resolution()
    await example4_scope_enforcement()
    await example5_default_type_inference()
    await example6_realistic_scenario()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
