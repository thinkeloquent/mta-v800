"""
Context resolver bridging template and compute function resolution.

Provides a unified API for resolving both {{variable.path}} templates
and {{fn:function_name}} compute functions.
"""

import re
from typing import Any, Dict, List, Optional

from .resolver import TemplateResolver
from .compute_registry import ComputeRegistry, ComputeFunctionError
from .interfaces import ResolverOptions


class ContextResolver:
    """
    Unified resolver for templates and compute functions.

    Automatically detects the pattern type and routes to the
    appropriate resolver.

    Example:
        registry = ComputeRegistry()
        registry.register("get_port", lambda: 5432)

        resolver = ContextResolver(registry)

        # Template resolution
        result = resolver.resolve("{{host}}", {"host": "localhost"})

        # Compute function resolution
        port = resolver.resolve("{{fn:get_port}}", {})

        # Mixed object resolution
        config = resolver.resolve_object({
            "host": "{{env.HOST}}",
            "port": "{{fn:get_port}}"
        }, {"env": {"HOST": "localhost"}})
    """

    # Pattern for compute functions: {{fn:function_name}}
    COMPUTE_PATTERN = re.compile(r'^\s*\{\{fn:(\w+)\}\}\s*$')

    def __init__(
        self,
        compute_registry: Optional[ComputeRegistry] = None,
        options: Optional[ResolverOptions] = None
    ) -> None:
        """
        Initialize the context resolver.

        Args:
            compute_registry: Registry of compute functions (optional)
            options: Default resolver options
        """
        self.template_resolver = TemplateResolver()
        self.compute_registry = compute_registry or ComputeRegistry()
        self.options = options

    def is_compute_pattern(self, expression: str) -> bool:
        """Check if expression is a compute function pattern."""
        return bool(self.COMPUTE_PATTERN.match(expression))

    def resolve(
        self,
        expression: str,
        context: Dict[str, Any],
        options: Optional[ResolverOptions] = None
    ) -> Any:
        """
        Resolve a template or compute expression.

        Args:
            expression: Template string or compute pattern
            context: Context for template resolution
            options: Override default resolver options

        Returns:
            Resolved value (string for templates, any for compute)

        Raises:
            ComputeFunctionError: If compute function not found
        """
        opts = options or self.options

        # Check for compute function pattern
        match = self.COMPUTE_PATTERN.match(expression)
        if match:
            fn_name = match.group(1)
            return self.compute_registry.resolve(fn_name, context)

        # Fall back to template resolution
        return self.template_resolver.resolve(expression, context, opts)

    def resolve_object(
        self,
        obj: Any,
        context: Dict[str, Any],
        options: Optional[ResolverOptions] = None
    ) -> Any:
        """
        Recursively resolve templates and compute functions in an object.

        Args:
            obj: Object containing template/compute expressions
            context: Context for template resolution
            options: Override default resolver options

        Returns:
            Object with all expressions resolved
        """
        if isinstance(obj, str):
            return self.resolve(obj, context, options)
        elif isinstance(obj, dict):
            return {
                k: self.resolve_object(v, context, options)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [
                self.resolve_object(item, context, options)
                for item in obj
            ]
        return obj

    def resolve_many(
        self,
        expressions: List[str],
        context: Dict[str, Any],
        options: Optional[ResolverOptions] = None
    ) -> List[Any]:
        """
        Resolve multiple expressions with the same context.

        Args:
            expressions: List of template/compute expressions
            context: Shared context for resolution
            options: Override default resolver options

        Returns:
            List of resolved values
        """
        return [
            self.resolve(expr, context, options)
            for expr in expressions
        ]
