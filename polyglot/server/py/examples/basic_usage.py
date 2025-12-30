#!/usr/bin/env python3
"""
Basic Usage Examples for Server Package

This script demonstrates the core features of the server package:
- Logger utility with multiple log levels
- Server initialization and configuration
- Request state management
- Lifecycle hooks

Run: python basic_usage.py
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from logger import logger, LoggerConfig, Logger
from server import init


# =============================================================================
# Example 1: Basic Logger Usage
# =============================================================================
def example1_basic_logging() -> None:
    """
    Demonstrates basic logger creation and usage.
    The logger provides a Console-like interface with log levels.
    """
    print("\n" + "=" * 60)
    print("Example 1: Basic Logger Usage")
    print("=" * 60)

    # Create a logger for this module
    log = logger.create("examples", __file__)

    # Log at different levels
    log.info("This is an info message")
    log.debug("This is a debug message (may not show at default level)")
    log.warn("This is a warning message")

    # Log with additional data
    log.info("Request received", {"method": "GET", "path": "/api/users"})

    # Log with error context
    try:
        raise ValueError("Something went wrong")
    except Exception as e:
        log.error("Operation failed", {"operation": "example"}, error=e)

    print("Logger example completed.\n")


# =============================================================================
# Example 2: Logger Configuration
# =============================================================================
def example2_logger_configuration() -> None:
    """
    Demonstrates logger configuration options.
    You can customize log level, colors, timestamps, and output format.
    """
    print("\n" + "=" * 60)
    print("Example 2: Logger Configuration")
    print("=" * 60)

    # Custom log level - only show debug and above
    log_debug = logger.create("examples", __file__, level="debug")
    log_debug.debug("This debug message will show")
    log_debug.trace("This trace message will NOT show (below debug level)")

    # JSON format output
    log_json = logger.create("examples", __file__, json_format=True)
    log_json.info("This message is in JSON format", {"format": "json"})

    # Disable colors
    log_no_color = logger.create("examples", __file__, colorize=False)
    log_no_color.info("This message has no ANSI colors")

    # Custom output function
    captured_logs = []
    log_custom = logger.create(
        "examples",
        __file__,
        output=lambda msg: captured_logs.append(msg)
    )
    log_custom.info("This message is captured")
    print(f"Captured log: {captured_logs[0][:50]}...")

    print("Logger configuration example completed.\n")


# =============================================================================
# Example 3: Child and Context Loggers
# =============================================================================
def example3_child_context_loggers() -> None:
    """
    Demonstrates child loggers and context loggers.
    Useful for maintaining package context while varying module/context.
    """
    print("\n" + "=" * 60)
    print("Example 3: Child and Context Loggers")
    print("=" * 60)

    # Create parent logger
    log = logger.create("myapp", __file__)

    # Create child logger for a sub-module
    child_log = log.child("submodule.py")
    child_log.info("Message from child logger (different filename)")

    # Create context logger with persistent context data
    request_log = log.with_context({"request_id": "abc-123", "user": "admin"})
    request_log.info("Processing request")
    request_log.info("Request completed", {"duration_ms": 45})

    print("Child and context logger example completed.\n")


# =============================================================================
# Example 4: Server Initialization
# =============================================================================
def example4_server_initialization() -> None:
    """
    Demonstrates server initialization with configuration.
    The init() function returns a FastAPI instance.
    """
    print("\n" + "=" * 60)
    print("Example 4: Server Initialization")
    print("=" * 60)

    # Basic server initialization
    config = {
        "title": "My API Server",
        "host": "127.0.0.1",
        "port": 8080,
    }

    app = init(config)
    print(f"Server initialized: {app.title}")

    # Add a simple route
    @app.get("/")
    async def root():
        return {"message": "Hello, World!"}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    print(f"Routes registered: {[r.path for r in app.routes if hasattr(r, 'path')]}")
    print("Server initialization example completed.\n")


# =============================================================================
# Example 5: Initial Request State
# =============================================================================
def example5_initial_request_state() -> None:
    """
    Demonstrates the initial_state feature.
    State is deep-cloned for each request, ensuring isolation.
    """
    print("\n" + "=" * 60)
    print("Example 5: Initial Request State")
    print("=" * 60)

    # Server with initial state
    config = {
        "title": "Stateful API",
        "initial_state": {
            "user": None,
            "permissions": [],
            "request_metadata": {
                "version": "1.0",
                "environment": "development",
            },
        },
    }

    app = init(config)
    print(f"Server initialized with initial_state keys: {list(config['initial_state'].keys())}")

    # The middleware will deep-clone this state for each request
    # This means mutations in one request won't affect others
    print("Each request gets a fresh deep copy of initial_state")
    print("Initial request state example completed.\n")


# =============================================================================
# Example 6: Lifecycle Hooks
# =============================================================================
def example6_lifecycle_hooks() -> None:
    """
    Demonstrates lifecycle hooks (onStartup/onShutdown).
    Hooks are loaded from modules in the lifecycle directory.
    """
    print("\n" + "=" * 60)
    print("Example 6: Lifecycle Hooks")
    print("=" * 60)

    # Create a temporary lifecycle directory with a hook module
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a lifecycle hook module
        lifecycle_file = Path(tmpdir) / "example_hooks.py"
        lifecycle_file.write_text('''
def onStartup(app, config):
    """Called when server starts."""
    print(f"  [Hook] Server starting: {config.get('title')}")
    # You can decorate the app, setup connections, etc.
    app.state.startup_time = "now"

async def onShutdown(app, config):
    """Called when server stops (can be async)."""
    print(f"  [Hook] Server stopping: {config.get('title')}")
    # Clean up resources, close connections, etc.
''')

        config = {
            "title": "Hooked API",
            "bootstrap": {
                "lifecycle": tmpdir,
            },
        }

        print(f"Created lifecycle hook at: {lifecycle_file}")
        print("Hooks will be executed by start() function:")
        print("  - onStartup: runs before server.listen()")
        print("  - onShutdown: runs on server.close()")

    print("Lifecycle hooks example completed.\n")


# =============================================================================
# Example 7: Environment Loading
# =============================================================================
def example7_environment_loading() -> None:
    """
    Demonstrates loading environment modules from a directory.
    Useful for loading .env files or setting up environment variables.
    """
    print("\n" + "=" * 60)
    print("Example 7: Environment Loading")
    print("=" * 60)

    # Create a temporary env directory with a loader module
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an env loader module
        env_file = Path(tmpdir) / "load_env.py"
        env_file.write_text('''
import os

# Set environment variables for the application
os.environ.setdefault("API_KEY", "development-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///dev.db")

print("  [Env] Environment variables loaded")
''')

        config = {
            "title": "Env-Loaded API",
            "bootstrap": {
                "load_env": tmpdir,
            },
        }

        print(f"Created env loader at: {env_file}")
        print("Env modules are executed during start() before lifecycle hooks")

    print("Environment loading example completed.\n")


# =============================================================================
# Example 8: Full Server Configuration
# =============================================================================
def example8_full_configuration() -> None:
    """
    Demonstrates a complete server configuration combining all features.
    This is a realistic example of production-like configuration.
    """
    print("\n" + "=" * 60)
    print("Example 8: Full Server Configuration")
    print("=" * 60)

    config = {
        # Basic server settings
        "title": "Production API",
        "host": "0.0.0.0",
        "port": 8080,
        "log_level": "info",

        # Initial request state (cloned per request)
        "initial_state": {
            "user": None,
            "authenticated": False,
            "permissions": [],
            "trace_id": None,
        },

        # Bootstrap configuration
        "bootstrap": {
            # "load_env": "./env",      # Load .env modules
            # "lifecycle": "./hooks",    # Load lifecycle hooks
        },
    }

    app = init(config)

    # Add middleware, routes, etc.
    @app.get("/api/v1/status")
    async def status():
        return {
            "service": config["title"],
            "status": "healthy",
            "version": "1.0.0",
        }

    print("Full configuration example:")
    print(f"  Title: {config['title']}")
    print(f"  Host: {config['host']}:{config['port']}")
    print(f"  Initial state keys: {list(config['initial_state'].keys())}")
    print("Full configuration example completed.\n")


# =============================================================================
# Main Runner
# =============================================================================
def main() -> None:
    """Run all examples sequentially."""
    print("\n" + "=" * 60)
    print("Server Package - Basic Usage Examples")
    print("=" * 60)

    # Set log level to debug for examples
    os.environ["LOG_LEVEL"] = "debug"

    examples = [
        example1_basic_logging,
        example2_logger_configuration,
        example3_child_context_loggers,
        example4_server_initialization,
        example5_initial_request_state,
        example6_lifecycle_hooks,
        example7_environment_loading,
        example8_full_configuration,
    ]

    for example_fn in examples:
        try:
            example_fn()
        except Exception as e:
            print(f"Example failed: {e}")

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
