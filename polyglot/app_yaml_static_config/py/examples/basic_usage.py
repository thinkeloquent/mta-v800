"""
Basic Usage Example for app_yaml_static_config

This script demonstrates the core functionality of the AppYamlConfig singleton,
including initialization, retrieving values, exploring usage of the SDK layer,
and verifying immutability.
"""

import sys
import os
from pathlib import Path
import asyncio

# Ensure we can import the package from src
sys.path.append(str(Path(__file__).parent.parent / "src"))

from app_yaml_static_config.core import AppYamlConfig
from app_yaml_static_config.sdk import AppYamlConfigSDK
from app_yaml_static_config.types import InitOptions
from app_yaml_static_config.validators import ImmutabilityError

FIXTURES_DIR = Path(__file__).parent.parent / "__fixtures__"


async def main():
    print("=============================================================================")
    print("App Yaml Static Config - Basic Usage Example")
    print("=============================================================================\n")

    await example1_initialization()
    example2_retrieving_values()
    example3_nested_access()
    example4_sdk_usage()
    example5_immutability()


# =============================================================================
# Example 1: Initialization
# =============================================================================
async def example1_initialization():
    """Demonstrates how to initialize the singleton with specific configuration files."""
    print("[Example 1] Initialization")

    # We point to the fixtures directory for demo purposes
    config_file = FIXTURES_DIR / "base.yaml"
    
    # Initialize the singleton
    # Note: In a real app, this is done once at startup
    options = InitOptions(
        files=[str(config_file)],
        config_dir=str(FIXTURES_DIR)
    )
    
    instance = AppYamlConfig.initialize(options)

    print("✅ Singleton initialized successfully.")
    print(f"   Config loaded from: {config_file}\n")


# =============================================================================
# Example 2: Retrieving Values
# =============================================================================
def example2_retrieving_values():
    """Demonstrates retrieving top-level values and using defaults."""
    print("[Example 2] Retrieving Values")
    
    config = AppYamlConfig.get_instance()
    
    # Get a known key
    app_config = config.get("app")
    print(f"   Value for 'app': {app_config}")

    # Get a missing key with default
    missing = config.get("non_existent_key", "default_value")
    print(f"   Value for 'non_existent_key' (defaulted): {missing}")
    print("")


# =============================================================================
# Example 3: Nested Access
# =============================================================================
def example3_nested_access():
    """Demonstrates accessing deeply nested keys safely."""
    print("[Example 3] Nested Access")
    
    config = AppYamlConfig.get_instance()
    
    # Using args for safe navigation
    app_name = config.get_nested("app", "name")
    print(f"   Value for ['app', 'name']: {app_name}")
    
    # Missing nested path with default
    deep_missing = config.get_nested("deeply", "missing", "path", default="fallback_val")
    print(f"   Value for missing nested path: {deep_missing}")
    print("")


# =============================================================================
# Example 4: SDK Usage
# =============================================================================
def example4_sdk_usage():
    """Demonstrates using the SDK layer for controlled access (e.g., for external tools)."""
    print("[Example 4] SDK Usage")
    
    sdk = AppYamlConfigSDK()
    
    # SDK methods mirror the main instance but are often used for tooling
    all_config = sdk.get_all()
    print(f"   SDK.get_all() keys: {list(all_config.keys())}")
    print("")


# =============================================================================
# Example 5: Immutability
# =============================================================================
def example5_immutability():
    """Demonstrates that the configuration cannot be modified at runtime."""
    print("[Example 5] Immutability Verification")
    
    config = AppYamlConfig.get_instance()
    
    try:
        print("   Attempting to set a new value...")
        config.set("new_key", "value")
    except ImmutabilityError as e:
        print(f"✅ Caught expected ImmutabilityError: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    print("")


if __name__ == "__main__":
    asyncio.run(main())
