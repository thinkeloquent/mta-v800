from typing import Any, Dict, List, Optional
# Import Protocol at runtime to avoid circular dep issues if possible, but typing needs it.
# We use 'TemplateResolverProtocol' forward reference or imports if using TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interfaces import TemplateResolverProtocol, ResolverOptions

def resolve_object(obj: Any, context: Dict[str, Any], resolver: "TemplateResolverProtocol", options: Optional["ResolverOptions"] = None, depth: int = 0) -> Any:
    if depth > 10:
        return obj

    if isinstance(obj, str):
        return resolver.resolve(obj, context, options)
    
    if isinstance(obj, list):
        return [resolve_object(item, context, resolver, options, depth + 1) for item in obj]
    
    if isinstance(obj, dict):
        return {k: resolve_object(v, context, resolver, options, depth + 1) for k, v in obj.items()}
    
    return obj
