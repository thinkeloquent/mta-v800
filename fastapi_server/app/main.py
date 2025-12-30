import asyncio
import importlib.util
import os
from pathlib import Path
from polyglot_server.server import init, start
from polyglot_server.autoload_routes import autoload_routes

# =============================================================================
# Pre-flight: Log critical ENV variables before any initialization
# =============================================================================
print("=" * 60)
print("FastAPI Server - Pre-flight Environment Check")
print("=" * 60)
print(f"  LOG_LEVEL         : {os.getenv('LOG_LEVEL', '(not set)')}")
print(f"  APP_ENV           : {os.getenv('APP_ENV', '(not set)')}")
print(f"  VAULT_SECRET_FILE : {os.getenv('VAULT_SECRET_FILE', '(not set)')}")
print(f"  CONFIG_DIR        : {os.getenv('CONFIG_DIR', '(not set)')}")
print(f"  PORT              : {os.getenv('PORT', '(not set)')}")
print("=" * 60)

# Determine paths relative to this file
# Assuming structure:
# root/
#   app/main.py
#   config/
#     env/
#     lifecycle/
BASE_DIR = Path(__file__).resolve().parent.parent

config = {
    "title": "FastAPI Integrated Server",
    "port": 8080,
    "bootstrap": {
        "load_env": str(BASE_DIR / "config" / "environment"),
        "lifecycle": str(BASE_DIR / "config" / "lifecycle"),
        "routes": str(BASE_DIR / "routes")
    }
}

# =============================================================================
# Bootstrap: Load environment modules at module level
# This must happen BEFORE app initialization so ENV vars are available
# =============================================================================
def _load_env_modules(env_dir: Path) -> None:
    """Load environment modules from directory (e.g., vault_file integration)."""
    if not env_dir.exists():
        print(f"[bootstrap] Warning: Environment directory not found: {env_dir}")
        return

    module_files = sorted(env_dir.glob("*.py"))
    print(f"[bootstrap] Loading {len(module_files)} environment module(s) from: {env_dir}")

    for module_path in module_files:
        print(f"[bootstrap]   Loading: {module_path.name}")
        try:
            spec = importlib.util.spec_from_file_location(module_path.stem, str(module_path))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
        except Exception as e:
            print(f"[bootstrap]   ERROR loading {module_path.name}: {e}")

def _load_lifecycle_modules(lifecycle_dir: Path) -> tuple:
    """Load lifecycle modules and extract startup/shutdown hooks."""
    startup_hooks = []
    shutdown_hooks = []

    if not lifecycle_dir.exists():
        print(f"[bootstrap] Warning: Lifecycle directory not found: {lifecycle_dir}")
        return startup_hooks, shutdown_hooks

    module_files = sorted(lifecycle_dir.glob("*.py"))
    print(f"[bootstrap] Loading {len(module_files)} lifecycle module(s) from: {lifecycle_dir}")

    for module_path in module_files:
        print(f"[bootstrap]   Loading: {module_path.name}")
        try:
            spec = importlib.util.spec_from_file_location(module_path.stem, str(module_path))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "onStartup"):
                    startup_hooks.append(module.onStartup)
                    print(f"[bootstrap]     Registered onStartup hook")
                if hasattr(module, "onShutdown"):
                    shutdown_hooks.append(module.onShutdown)
                    print(f"[bootstrap]     Registered onShutdown hook")
        except Exception as e:
            print(f"[bootstrap]   ERROR loading {module_path.name}: {e}")

    return startup_hooks, shutdown_hooks

# Load environment modules first (VaultFile, etc.)
_load_env_modules(Path(config["bootstrap"]["load_env"]))

# Load lifecycle modules and capture hooks
_startup_hooks, _shutdown_hooks = _load_lifecycle_modules(Path(config["bootstrap"]["lifecycle"]))

print(f"[bootstrap] Hooks registered: {len(_startup_hooks)} startup, {len(_shutdown_hooks)} shutdown")
print("=" * 60)

# =============================================================================
# Create FastAPI app at module level for uvicorn to import
# =============================================================================
app = init(config)

# Store hooks in app.state for lifespan to execute
app.state.startup_hooks = _startup_hooks
app.state.shutdown_hooks = _shutdown_hooks
app.state.config = config

# Load routes at module level for uvicorn --reload compatibility
autoload_routes(app, config.get("bootstrap", {}))

print("[bootstrap] FastAPI Server initialization complete")
print("=" * 60)

if __name__ == "__main__":
    # Start (Bootstrap + Serve) - when running directly
    asyncio.run(start(app, config))
