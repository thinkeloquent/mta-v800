#!/usr/bin/env python3
"""
app_yaml_overwrites - Basic Usage Examples
==========================================

This script demonstrates core features of the app_yaml_overwrites package:
- Logger: Standardized JSON logging with LOG_LEVEL control
- ContextBuilder: Building resolution context with extenders
- OverwriteMerger: Deep merging configuration overwrites

Run with: python basic_usage.py
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add parent src to path for direct execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'app_yaml_overwrites'))

# Import directly from modules (bypassing __init__.py which has external deps)
from logger import Logger
from context_builder import ContextBuilder
from overwrite_merger import apply_overwrites


# =============================================================================
# Example 1: Logger Factory Pattern
# =============================================================================
def example1_logger_factory() -> None:
    """
    Demonstrates the Logger.create() factory pattern for standardized logging.

    The logger outputs JSON-formatted logs with:
    - timestamp
    - level (DEBUG, INFO, WARN, ERROR)
    - context (package:filename)
    - message
    - data (optional kwargs)
    """
    print("\n" + "=" * 60)
    print("Example 1: Logger Factory Pattern")
    print("=" * 60)

    # Create logger using factory pattern
    logger = Logger.create("my-service", "basic_usage.py")

    # Log at different levels
    logger.debug("This is a debug message")
    logger.info("Application started", version="1.0.0", env="development")
    logger.warn("Configuration missing, using defaults")
    logger.error("Failed to connect", host="localhost", port=5432)

    print("\nLogger created with context: my-service:basic_usage.py")


# =============================================================================
# Example 2: Log Level Control
# =============================================================================
def example2_log_level_control() -> None:
    """
    Demonstrates LOG_LEVEL environment variable control.

    Levels (in order): trace, debug, info, warn, error
    Setting LOG_LEVEL=info will suppress debug and trace messages.
    """
    print("\n" + "=" * 60)
    print("Example 2: Log Level Control")
    print("=" * 60)

    # Store original level
    original_level = os.environ.get("LOG_LEVEL")

    # Set to INFO level - should suppress DEBUG
    os.environ["LOG_LEVEL"] = "info"
    logger = Logger.create("log-demo", "basic_usage.py")

    print("\nWith LOG_LEVEL=info:")
    logger.debug("This DEBUG message should be suppressed")
    logger.info("This INFO message should appear")

    # Set to ERROR level - should only show errors
    os.environ["LOG_LEVEL"] = "error"
    logger2 = Logger.create("log-demo-2", "basic_usage.py")

    print("\nWith LOG_LEVEL=error:")
    logger2.info("This INFO message should be suppressed")
    logger2.error("This ERROR message should appear")

    # Restore original level
    if original_level:
        os.environ["LOG_LEVEL"] = original_level
    else:
        os.environ.pop("LOG_LEVEL", None)


# =============================================================================
# Example 3: Context Builder - Basic Usage
# =============================================================================
async def example3_context_builder_basic() -> None:
    """
    Demonstrates building a resolution context with ContextBuilder.

    The context contains:
    - env: Environment variables (defaults to os.environ)
    - config: Raw configuration dictionary
    - app: Application metadata
    - state: Runtime state
    - request: HTTP request object (optional)
    """
    print("\n" + "=" * 60)
    print("Example 3: Context Builder - Basic Usage")
    print("=" * 60)

    # Build context with basic options
    context = await ContextBuilder.build({
        "config": {
            "app": {"name": "MyApp", "version": "1.0.0"},
            "database": {"host": "localhost", "port": 5432}
        },
        "app": {"name": "MyApp", "version": "1.0.0"},
        "state": {"request_count": 42}
    })

    print(f"\nContext keys: {list(context.keys())}")
    print(f"App name: {context['app']['name']}")
    print(f"State: {context['state']}")
    print(f"Has env: {'env' in context}")


# =============================================================================
# Example 4: Context Builder - With Extenders
# =============================================================================
async def example4_context_builder_extenders() -> None:
    """
    Demonstrates context extenders for adding custom context.

    Extenders are async functions that receive the current context
    and optionally the request, returning additional context keys.
    They run sequentially and can see results from previous extenders.
    """
    print("\n" + "=" * 60)
    print("Example 4: Context Builder - With Extenders")
    print("=" * 60)

    # Define auth extender - adds authentication context
    async def auth_extender(ctx: Dict[str, Any], request: Any) -> Dict[str, Any]:
        # Simulate fetching auth from request headers or session
        return {
            "auth": {
                "user_id": "user-123",
                "roles": ["admin", "user"],
                "token": "bearer-xxx"
            }
        }

    # Define tenant extender - adds multi-tenancy context
    async def tenant_extender(ctx: Dict[str, Any], request: Any) -> Dict[str, Any]:
        # Can access auth from previous extender
        user_id = ctx.get("auth", {}).get("user_id", "anonymous")
        return {
            "tenant": {
                "id": "tenant-456",
                "name": "Acme Corp",
                "owner": user_id
            }
        }

    # Build context with extenders
    context = await ContextBuilder.build(
        {"config": {"app": {"name": "MultiTenantApp"}}},
        extenders=[auth_extender, tenant_extender]
    )

    print(f"\nContext keys: {list(context.keys())}")
    print(f"Auth user: {context['auth']['user_id']}")
    print(f"Tenant: {context['tenant']['name']}")
    print(f"Tenant owner: {context['tenant']['owner']}")


# =============================================================================
# Example 5: Overwrite Merger - Basic Merge
# =============================================================================
def example5_overwrite_merger_basic() -> None:
    """
    Demonstrates basic configuration merging with apply_overwrites.

    The merge is deep - nested dictionaries are merged recursively,
    with overwrites taking precedence.
    """
    print("\n" + "=" * 60)
    print("Example 5: Overwrite Merger - Basic Merge")
    print("=" * 60)

    # Original configuration with some null placeholders
    original = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "password": None  # Placeholder for runtime value
        },
        "cache": {
            "enabled": True,
            "ttl": 3600
        }
    }

    # Overwrites to apply (e.g., from resolved templates)
    overwrites = {
        "database": {
            "password": "secret-from-vault"  # Fill in the placeholder
        },
        "cache": {
            "ttl": 7200  # Override default TTL
        }
    }

    result = apply_overwrites(original, overwrites)

    print(f"\nOriginal password: {original['database']['password']}")
    print(f"Merged password: {result['database']['password']}")
    print(f"Original TTL: {original['cache']['ttl']}")
    print(f"Merged TTL: {result['cache']['ttl']}")
    print(f"Host preserved: {result['database']['host']}")


# =============================================================================
# Example 6: Overwrite Merger - overwrite_from_context Pattern
# =============================================================================
def example6_overwrite_from_context() -> None:
    """
    Demonstrates the overwrite_from_context pattern used in app.yaml.

    This pattern allows configurations to define which values should
    be resolved at runtime and merged back into the parent config.
    """
    print("\n" + "=" * 60)
    print("Example 6: overwrite_from_context Pattern")
    print("=" * 60)

    # Provider configuration with overwrite_from_context section
    provider_config = {
        "base_url": "https://api.example.com",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": None,  # Will be filled from context
            "X-App-Name": None      # Will be filled from context
        },
        "timeout": 30,
        "overwrite_from_context": {
            "headers": {
                "Authorization": "Bearer resolved-jwt-token",
                "X-App-Name": "MyApp"
            }
        }
    }

    # Apply the overwrites (simulating what the resolver does)
    resolved = apply_overwrites(
        provider_config,
        provider_config.get("overwrite_from_context", {})
    )

    print("\nBefore merge:")
    print(f"  Authorization: {provider_config['headers']['Authorization']}")
    print(f"  X-App-Name: {provider_config['headers']['X-App-Name']}")

    print("\nAfter merge:")
    print(f"  Authorization: {resolved['headers']['Authorization']}")
    print(f"  X-App-Name: {resolved['headers']['X-App-Name']}")
    print(f"  Content-Type (preserved): {resolved['headers']['Content-Type']}")


# =============================================================================
# Example 7: Full Integration Pattern
# =============================================================================
async def example7_full_integration() -> None:
    """
    Demonstrates combining all components in a realistic scenario.

    This shows how the pieces work together:
    1. Logger for observability
    2. ContextBuilder for preparing resolution context
    3. OverwriteMerger for applying resolved values
    """
    print("\n" + "=" * 60)
    print("Example 7: Full Integration Pattern")
    print("=" * 60)

    # Setup logger
    logger = Logger.create("integration-demo", "basic_usage.py")
    logger.info("Starting configuration resolution")

    # Simulate raw configuration (would come from AppYamlConfig)
    raw_config = {
        "app": {"name": "IntegrationDemo", "version": "2.0.0"},
        "providers": {
            "payment_api": {
                "base_url": "https://pay.example.com",
                "headers": {
                    "X-Api-Key": None,
                    "X-Tenant-Id": None
                },
                "overwrite_from_context": {
                    "headers": {
                        "X-Api-Key": "{{env.PAYMENT_API_KEY}}",
                        "X-Tenant-Id": "{{tenant.id}}"
                    }
                }
            }
        }
    }

    # Define context extenders
    async def api_key_extender(ctx, req):
        # Simulate resolving API key from secrets
        return {"secrets": {"payment_api_key": "sk_live_xxx"}}

    async def tenant_extender(ctx, req):
        return {"tenant": {"id": "tenant-789"}}

    # Build context
    context = await ContextBuilder.build(
        {
            "config": raw_config,
            "app": raw_config["app"],
            "env": {"PAYMENT_API_KEY": "sk_live_xxx"}
        },
        extenders=[api_key_extender, tenant_extender]
    )

    logger.debug("Context built", keys=list(context.keys()))

    # Simulate resolved overwrites (in real use, RuntimeTemplateResolver does this)
    resolved_overwrites = {
        "headers": {
            "X-Api-Key": context["env"]["PAYMENT_API_KEY"],
            "X-Tenant-Id": context["tenant"]["id"]
        }
    }

    # Apply overwrites
    provider = raw_config["providers"]["payment_api"]
    resolved_provider = apply_overwrites(provider, resolved_overwrites)

    logger.info("Configuration resolved", provider="payment_api")

    print(f"\nResolved payment_api provider:")
    print(f"  Base URL: {resolved_provider['base_url']}")
    print(f"  X-Api-Key: {resolved_provider['headers']['X-Api-Key']}")
    print(f"  X-Tenant-Id: {resolved_provider['headers']['X-Tenant-Id']}")


# =============================================================================
# Main Runner
# =============================================================================
async def main() -> None:
    """Run all examples sequentially."""
    print("=" * 60)
    print("app_yaml_overwrites - Basic Usage Examples")
    print("=" * 60)

    # Synchronous examples
    example1_logger_factory()
    example2_log_level_control()

    # Async examples
    await example3_context_builder_basic()
    await example4_context_builder_extenders()

    # Synchronous examples
    example5_overwrite_merger_basic()
    example6_overwrite_from_context()

    # Full integration
    await example7_full_integration()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
