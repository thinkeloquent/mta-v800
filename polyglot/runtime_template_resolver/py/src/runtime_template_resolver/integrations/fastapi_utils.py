from typing import Callable, Any, Dict, Optional, Protocol
from fastapi import Request
from ..resolver import TemplateResolver
from ..interfaces import ResolverOptions

class ConfiguredResolverProtocol(Protocol):
    def resolve(self, template: str, context: Dict[str, Any]) -> str: ...
    def resolve_object(self, obj: Any, context: Dict[str, Any]) -> Any: ...

def create_resolver_dependency(options: Optional[ResolverOptions] = None) -> Callable[[Request], ConfiguredResolverProtocol]:
    """
    Creates a dependency that returns a configured TemplateResolver.
    """
    resolver = TemplateResolver()
    
    def get_resolver(request: Request) -> ConfiguredResolverProtocol:
        # We wrap the resolver to pre-apply options/logger if needed
        class ConfiguredResolver:
             def resolve(self, template: str, context: Dict[str, Any]) -> str:
                 return resolver.resolve(template, context, options=options)
             
             def resolve_object(self, obj: Any, context: Dict[str, Any]) -> Any:
                 return resolver.resolve_object(obj, context, options=options)
        
        return ConfiguredResolver()

    return get_resolver
