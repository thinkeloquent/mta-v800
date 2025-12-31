"""
Compute function registry for runtime template resolution.

Provides registration and execution of compute functions
used with the {{fn:function_name}} pattern.
"""

import re
from typing import Any, Callable, Dict, List, Optional
from enum import Enum


class ComputeScope(Enum):
    """Scope for compute function execution."""
    STARTUP = "startup"   # Resolved once at application startup
    REQUEST = "request"   # Resolved per request


class ComputeFunctionError(Exception):
    """Raised when compute function execution fails."""
    pass


class ComputeRegistry:
    """
    Registry for compute functions.

    Example:
        registry = ComputeRegistry()
        registry.register("get_timestamp", lambda: datetime.now().isoformat())
        registry.register("get_port", lambda ctx: ctx.get("PORT", 3000))

        value = registry.resolve("get_timestamp")  # "2024-01-01T00:00:00"
    """

    # Valid function name pattern: starts with letter or underscore, followed by alphanumerics/underscores
    _NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    def __init__(self) -> None:
        self._functions: Dict[str, tuple[Callable[..., Any], ComputeScope]] = {}

    def register(
        self,
        name: str,
        fn: Callable[..., Any],
        scope: ComputeScope = ComputeScope.STARTUP
    ) -> None:
        """
        Register a compute function.

        Args:
            name: Function name (used in {{fn:name}} pattern)
            fn: Callable that takes optional context and returns a value
            scope: When the function should be evaluated

        Raises:
            ValueError: If name is invalid or already registered
        """
        if not name or not self._NAME_PATTERN.match(name):
            raise ValueError(f"Invalid function name: {name}")

        if name in self._functions:
            raise ValueError(f"Function already registered: {name}")

        self._functions[name] = (fn, scope)

    def resolve(
        self,
        name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute a registered compute function.

        Args:
            name: Function name to execute
            context: Optional context passed to the function

        Returns:
            Result of function execution

        Raises:
            ComputeFunctionError: If function not found or execution fails
        """
        if name not in self._functions:
            raise ComputeFunctionError(f"Unknown compute function: {name}")

        fn, scope = self._functions[name]

        try:
            # Functions can optionally accept context
            if context is not None:
                try:
                    return fn(context)
                except TypeError:
                    # Function doesn't accept context argument
                    return fn()
            return fn()
        except Exception as e:
            raise ComputeFunctionError(
                f"Error executing compute function '{name}': {e}"
            ) from e

    def has(self, name: str) -> bool:
        """Check if a function is registered."""
        return name in self._functions

    def list(self) -> List[str]:
        """List all registered function names."""
        return list(self._functions.keys())

    def get_scope(self, name: str) -> Optional[ComputeScope]:
        """Get the scope of a registered function."""
        if name in self._functions:
            return self._functions[name][1]
        return None

    def unregister(self, name: str) -> bool:
        """
        Unregister a compute function.

        Args:
            name: Function name to unregister

        Returns:
            True if function was unregistered, False if not found
        """
        if name in self._functions:
            del self._functions[name]
            return True
        return False

    def clear(self) -> None:
        """Remove all registered functions."""
        self._functions.clear()
