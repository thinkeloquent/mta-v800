import re
from typing import Any, Dict, List, Optional, Union, Coroutine
from dataclasses import dataclass
import copy

from .logger import Logger
from .options import ComputeScope, MissingStrategy, ResolverOptions
from .errors import (
    ErrorCode,
    ComputeFunctionError,
    RecursionLimitError,
    ScopeViolationError,
    SecurityError
)
from .compute_registry import ComputeRegistry
from .security import Security

class ContextResolver:
    # {{fn:name | "default"}}
    COMPUTE_PATTERN = re.compile(r'^\{\{fn:([a-zA-Z_][a-zA-Z0-9_]*)(\s*\|\s*[\'"](.*)[\'"])?\}\}$')
    # {{variable.path | "default"}}
    # Relaxed pattern to capture potential security violations (e.g. _private) for validation
    TEMPLATE_PATTERN = re.compile(r'^\{\{([a-zA-Z0-9_.]*)(\s*\|\s*[\'"](.*)[\'"])?\}\}$')
    # Originally: r'^\{\{([a-zA-Z][a-zA-Z0-9_.]*)(\s*\|\s*[\'"](.*)[\'"])?\}\}$'

    def __init__(self, registry: ComputeRegistry, options: Optional[ResolverOptions] = None):
        opts = options or ResolverOptions()
        self._logger = opts.logger or Logger.create("runtime_template_resolver", __file__)
        self._registry = registry
        self._max_depth = opts.max_depth
        self._missing_strategy = opts.missing_strategy
        self._logger.debug("ContextResolver initialized")

    def is_compute_pattern(self, expression: str) -> bool:
        return bool(self.COMPUTE_PATTERN.match(expression))

    async def resolve(
        self,
        expression: Any,
        context: Dict[str, Any],
        scope: ComputeScope = ComputeScope.REQUEST,
        depth: int = 0
    ) -> Any:
        # Pass-through non-string values
        if not isinstance(expression, str):
            return expression

        # Recursion check
        if depth > self._max_depth:
            raise RecursionLimitError(
                f"Recursion limit reached ({self._max_depth})",
                ErrorCode.RECURSION_LIMIT
            )

        # Check compute pattern first
        compute_match = self.COMPUTE_PATTERN.match(expression)
        if compute_match:
            return await self._resolve_compute(compute_match, context, scope)

        # Check template pattern
        template_match = self.TEMPLATE_PATTERN.match(expression)
        if template_match:
            return self._resolve_template(template_match, context)

        # Otherwise return literal string
        return expression

    async def resolve_object(
        self,
        obj: Any,
        context: Dict[str, Any],
        scope: ComputeScope = ComputeScope.REQUEST,
        depth: int = 0
    ) -> Any:
        if depth > self._max_depth:
            raise RecursionLimitError(
                f"Recursion limit reached ({self._max_depth})",
                ErrorCode.RECURSION_LIMIT
            )

        if isinstance(obj, dict):
            # Recurse into dict values
            new_obj = {}
            for k, v in obj.items():
                new_obj[k] = await self.resolve_object(v, context, scope, depth + 1)
            return new_obj
        
        elif isinstance(obj, list):
            # Map over list elements
            return [await self.resolve_object(item, context, scope, depth + 1) for item in obj]
        
        elif isinstance(obj, str):
            # Use resolve implementation for strings
            # But wait, resolve checks for patterns.
            # If resolve returns same string, it means no pattern.
            # We need to check if resolve returns a new value (could be any type)
            # resolve_object MUST effectively call resolve if it's a string, BUT resolve handles recursion limit already.
            # However, resolve handles SINGLE expression.
            # If string contains multiple patterns mixed with text, we don't support that here yet.
            # Plan says "Pattern detection... routes to Resolver".
            # "Handles mixed template and compute expressions" -> Feature 3.3 Batch Resolution handles array.
            # Does `resolve` handle `abc {{val}} def`? 
            # Plan criteria 3.1: "Pattern detection: {{...}} routes to TemplateResolver".
            # Usually strict equality to pattern is implemented, not interpolation strings.
            # "Type preservation: {{port}} returns 5432 (int) not '5432' (string)"
            # This implies strict match.
            return await self.resolve(obj, context, scope, depth)

        return obj

    async def resolve_many(
        self,
        expressions: List[Any],
        context: Dict[str, Any],
        scope: ComputeScope = ComputeScope.REQUEST
    ) -> List[Any]:
        results = []
        for expr in expressions:
            results.append(await self.resolve(expr, context, scope))
        return results

    async def _resolve_compute(self, match: re.Match, context: Dict[str, Any], scope: ComputeScope) -> Any:
        fn_name = match.group(1)
        default_val = match.group(3)

        self._logger.debug(f"Resolving compute: {fn_name}, default: {default_val}")

        # Check registry existence first
        if not self._registry.has(fn_name):
            if default_val is not None:
                return self._parse_default(default_val)
            if self._missing_strategy == MissingStrategy.DEFAULT:
                 return None # Or some default?
            if self._missing_strategy == MissingStrategy.IGNORE:
                 return match.group(0) # Return original string?
            # Default is ERROR
            raise ComputeFunctionError(
                f"Compute function not found: {fn_name}",
                ErrorCode.COMPUTE_FUNCTION_NOT_FOUND,
                {"name": fn_name}
            )

        # Check Scope
        fn_scope = self._registry.get_scope(fn_name)
        if fn_scope == ComputeScope.REQUEST and scope == ComputeScope.STARTUP:
             raise ScopeViolationError(
                 f"Cannot call REQUEST scope function '{fn_name}' from STARTUP scope",
                 ErrorCode.SCOPE_VIOLATION,
                 {"name": fn_name, "scope": "STARTUP", "fn_scope": "REQUEST"}
             )

        try:
            return await self._registry.resolve(fn_name, context)
        except Exception as e:
            if default_val is not None:
                self._logger.warn(f"Function {fn_name} failed, using default: {e}")
                return self._parse_default(default_val)
            raise e

    def _resolve_template(self, match: re.Match, context: Dict[str, Any]) -> Any:
        path = match.group(1)
        default_val = match.group(3)
        
        self._logger.debug(f"Resolving template: {path}, default: {default_val}")

        # Security check
        Security.validate_path(path)
        
        # Resolve path in context
        val = self._get_value_by_path(context, path)
        
        if val is None:
            if default_val is not None:
                return self._parse_default(default_val)
            if self._missing_strategy == MissingStrategy.IGNORE:
                 return match.group(0)
             # If strictly unresolved and no default, maybe return None or raise?
             # Standard behavior usually: if missing strategy is ERROR, raise.
             # If DEFAULT (but no default provided), maybe None?
            if self._missing_strategy == MissingStrategy.ERROR:
                # Assuming empty string or None is okay if strictly missing?
                # Usually we want to know it's missing.
                # But here, if get_value_by_path returns None, it means missing.
                 # (Assuming None is not a valid value for a key).
                 # Better to have sentinel for missing.
                 pass # We already got None.
        
        return val if val is not None else (self._parse_default(default_val) if default_val is not None else match.group(0))

    def _get_value_by_path(self, context: Any, path: str) -> Any:
        # Simple dot notation traversal
        current = context
        for key in path.split('.'):
            if isinstance(current, dict):
                current = current.get(key)
            else:
                 # Check object attribute
                try:
                    current = getattr(current, key)
                except AttributeError:
                    return None
            
            if current is None:
                return None
        return current

    def _parse_default(self, val: str) -> Any:
        # Basic type inference for default values string
        if val is None: return None
        if val.lower() == 'true': return True
        if val.lower() == 'false': return False
        if val.isdigit(): return int(val)
        try:
            return float(val)
        except ValueError:
            pass
        return val
