"""
Runtime Template Resolver Package
"""
from .interfaces import (
    TemplateResolverProtocol,
    ResolverOptions,
    MissingStrategy,
    ResolverResult
)
from .errors import SecurityError, ValidationError, MissingValueError
from .logger import logger, LoggerProtocol
from .resolver import TemplateResolver
from .sdk import resolve, resolve_many, resolve_object, validate, extract, compile
from .validator import validate_placeholder
from .extractor import extract_placeholders
from .missing_handler import handle_missing
from .compiler import compile as compile_template
from .compute_registry import ComputeRegistry, ComputeScope, ComputeFunctionError
from .context_resolver import ContextResolver

__all__ = [
    "TemplateResolverProtocol",
    "ResolverOptions",
    "MissingStrategy",
    "ResolverResult",
    "SecurityError",
    "ValidationError",
    "MissingValueError",
    "logger",
    "LoggerProtocol",
    "TemplateResolver",
    "resolve",
    "resolve_many",
    "resolve_object",
    "validate",
    "extract",
    "compile",
    "validate_placeholder",
    "extract_placeholders",
    "handle_missing",
    "compile_template",
    "ComputeRegistry",
    "ComputeScope",
    "ComputeFunctionError",
    "ContextResolver",
]
