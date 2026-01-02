import re
import asyncio
from typing import Callable, Dict, Optional, Any, List, Union
from dataclasses import dataclass

from .logger import Logger
from .options import ComputeScope
from .errors import ComputeFunctionError, ErrorCode

@dataclass
class RegisteredFunction:
    fn: Callable
    scope: ComputeScope

class ComputeRegistry:
    NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    def __init__(self, logger: Optional[Logger] = None):
        self._logger = logger or Logger.create("runtime_template_resolver", __file__)
        self._functions: Dict[str, RegisteredFunction] = {}
        self._cache: Dict[str, Any] = {}
        self._logger.debug("ComputeRegistry initialized")

    def register(self, name: str, fn: Callable, scope: ComputeScope) -> None:
        self._validate_name(name)
        self._logger.debug(f"Registering function: {name} with scope: {scope}")
        self._functions[name] = RegisteredFunction(fn=fn, scope=scope)
        self._logger.info(f"Function registered: {name}")

    def unregister(self, name: str) -> None:
        if name in self._functions:
            self._logger.debug(f"Unregistering function: {name}")
            del self._functions[name]
            self._logger.info(f"Function unregistered: {name}")

    def has(self, name: str) -> bool:
        return name in self._functions

    def list(self) -> List[str]:
        return list(self._functions.keys())

    def get_scope(self, name: str) -> Optional[ComputeScope]:
        if name in self._functions:
            return self._functions[name].scope
        return None

    def clear(self) -> None:
        self._logger.debug("Clearing registry")
        self._functions.clear()
        self._cache.clear()

    def clear_cache(self) -> None:
        self._logger.debug("Clearing result cache")
        self._cache.clear()

    async def resolve(self, name: str, context: Optional[Dict[str, Any]] = None) -> Any:
        self._logger.debug(f"Resolving function: {name}")
        
        if name not in self._functions:
            raise ComputeFunctionError(
                f"Compute function not found: {name}",
                ErrorCode.COMPUTE_FUNCTION_NOT_FOUND,
                {"name": name}
            )

        reg_fn = self._functions[name]

        # Check cache for STARTUP functions
        if reg_fn.scope == ComputeScope.STARTUP and name in self._cache:
            self._logger.debug(f"Returning cached value for: {name}")
            return self._cache[name]

        try:
            # Check if function expects arguments
            # Simple check for now, can be more robust with signature inspection
            # Assuming fn(context) or fn()
            
            result = None
            if asyncio.iscoroutinefunction(reg_fn.fn):
                try:
                    result = await reg_fn.fn(context)
                except TypeError:
                     # Fallback if it doesn't accept context
                    result = await reg_fn.fn()
            else:
                try:
                    result = reg_fn.fn(context)
                except TypeError:
                     # Fallback if it doesn't accept context
                    result = reg_fn.fn()
            
            # Cache result if STARTUP scope
            if reg_fn.scope == ComputeScope.STARTUP:
                self._cache[name] = result

            return result

        except Exception as e:
            self._logger.error(f"Function execution failed: {name}, error: {str(e)}")
            raise ComputeFunctionError(
                f"Compute function failed: {name}",
                ErrorCode.COMPUTE_FUNCTION_FAILED,
                {"name": name, "original_error": str(e)}
            ) from e

    def _validate_name(self, name: str) -> None:
        if not name:
             raise ValueError("Function name cannot be empty")
        if not self.NAME_PATTERN.match(name):
            raise ValueError(f"Invalid function name: {name}. Must match pattern: ^[a-zA-Z_][a-zA-Z0-9_]*$")
