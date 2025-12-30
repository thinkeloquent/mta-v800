"""
Basic usage examples for vault_file package.

This package provides Vault File management and Environment Store logic.
"""
import os
import sys

# Boilerplate to allow running this script directly without installing the package
# Assumes structure: .../py/examples/basic_usage.py -> .../py/src
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from vault_file import VaultFileSDK, EnvStore

DEMO_ENV_FILE = os.path.join(os.path.dirname(__file__), ".env.demo")

def setup_demo_env():
    """Create a dummy .env file for demonstration."""
    with open(DEMO_ENV_FILE, "w") as f:
        f.write("EXAMPLE_VAR=hello_python\\nANOTHER_VAR=bar_baz\\n")

def cleanup_demo_env():
    """Remove the dummy .env file."""
    if os.path.exists(DEMO_ENV_FILE):
        os.remove(DEMO_ENV_FILE)

# =============================================================================
# Example 1: SDK Initialization and Config Loading
# =============================================================================
def example1_load_config() -> None:
    """Initialize the SDK and load configuration from a specific .env file."""
    print("--- Example 1: Load Config ---")
    
    # Create SDK instance using builder
    sdk = VaultFileSDK.create().with_env_path(DEMO_ENV_FILE).build()

    # Load config (initializes EnvStore)
    result = sdk.load_config()

    if result.success:
        print(f"Config loaded successfully: {result.data}")
    else:
        print(f"Failed to load config: {result.error}")


# =============================================================================
# Example 2: Accessing Secrets Wrapper
# =============================================================================
def example2_access_secrets() -> None:
    """Use the SDK helper to safely access secrets with masking support."""
    print("\\n--- Example 2: Access Secrets ---")

    # Re-use default SDK instance (EnvStore is singleton, already initialized in Ex 1)
    sdk = VaultFileSDK.create().build()

    result = sdk.get_secret_safe("EXAMPLE_VAR")
    if result.success and result.data:
        print(f"Key: {result.data.key}")
        print(f"Exists: {result.data.exists}")
        print(f"Masked Value: {result.data.masked}")


# =============================================================================
# Example 3: Direct EnvStore Usage
# =============================================================================
def example3_env_store_usage() -> None:
    """Access variables directly via the EnvStore singleton for zero-overhead reads."""
    print("\\n--- Example 3: Direct EnvStore Usage ---")

    # Get value or default
    val = EnvStore.get("NON_EXISTENT", "default_value")
    print(f"Got with default: {val}")

    # Get existing value
    existing = EnvStore.get("EXAMPLE_VAR")
    print(f"Got existing: {existing}")

    # Get or throw
    try:
        required = EnvStore.get_or_throw("EXAMPLE_VAR")
        print(f"Got required: {required}")
    except Exception as e:
        print(f"Error getting required: {e}")


# =============================================================================
# Example 4: File Validation
# =============================================================================
def example4_validation() -> None:
    """Validate a vault file or env file without loading it into the store."""
    print("\\n--- Example 4: Validation ---")

    sdk = VaultFileSDK.create().build()
    validation = sdk.validate_file(DEMO_ENV_FILE)

    if validation.success and validation.data:
        print(f"File {os.path.basename(DEMO_ENV_FILE)} valid: {validation.data.valid}")


# =============================================================================
# Main Runner
# =============================================================================
def main():
    try:
        setup_demo_env()
        
        example1_load_config()
        example2_access_secrets()
        example3_env_store_usage()
        example4_validation()
        
    except Exception as e:
        print(f"Unhandled error in examples: {e}")
    finally:
        cleanup_demo_env()

if __name__ == "__main__":
    main()
