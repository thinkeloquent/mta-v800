from typing import Optional

from .logger import Logger
from .options import ResolverOptions
from .compute_registry import ComputeRegistry
from .context_resolver import ContextResolver

def create_registry(logger: Optional[Logger] = None) -> ComputeRegistry:
    """Factory function to create a new ComputeRegistry"""
    return ComputeRegistry(logger=logger)

def create_resolver(
    registry: Optional[ComputeRegistry] = None,
    options: Optional[ResolverOptions] = None,
    logger: Optional[Logger] = None
) -> ContextResolver:
    """Factory function to create a new ContextResolver"""
    reg = registry or create_registry(logger=logger)
    
    # If logger provided but not in options, create default options with logger
    if logger and not options:
        options = ResolverOptions(logger=logger)
    elif logger and options and not options.logger:
        # Override logger in options if passed explicitly but missing in options
        options.logger = logger
        
    return ContextResolver(registry=reg, options=options)
