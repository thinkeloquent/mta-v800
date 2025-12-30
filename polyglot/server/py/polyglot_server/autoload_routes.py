import importlib.util
from pathlib import Path
from typing import Any, Dict
from fastapi import FastAPI
from .logger import logger

log = logger.create("autoload_routes", __file__)

def autoload_routes(server: FastAPI, bootstrap: Dict[str, Any]) -> None:
    """
    Autoload route modules from the configured directory.
    Modules must export a 'mount(app)' function.
    """
    if bootstrap.get("routes"):
        routes_dir = Path(bootstrap["routes"])
        log.debug("Loading route modules", {"path": str(routes_dir)})
        if routes_dir.exists():
            module_files = sorted(routes_dir.glob("*.py"))
            log.trace("Found route modules", {"count": len(module_files), "files": [str(f) for f in module_files]})
            for module_path in module_files:
                log.debug("Loading route module", {"module": str(module_path)})
                try:
                    spec = importlib.util.spec_from_file_location(module_path.stem, str(module_path))
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        if hasattr(module, "mount"):
                            log.trace("Mounting route module", {"module": module.__name__})
                            module.mount(server)
                        else:
                            log.warn("Route module does not export 'mount' function", {"module": str(module_path)})
                except Exception as e:
                    log.error("Failed to load route module", {"module": str(module_path), "error": str(e)})
                    
            log.info("Route modules loaded", {"count": len(module_files)})
        else:
            log.warn("Routes directory does not exist", {"path": str(routes_dir)})
