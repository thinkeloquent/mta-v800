import os
from typing import Dict, Any, Optional, List, Callable, Awaitable

ContextExtender = Callable[[Dict[str, Any], Optional[Any]], Awaitable[Dict[str, Any]]]

class ContextBuilder:
    @staticmethod
    async def build(
        options: Dict[str, Any], 
        extenders: List[ContextExtender] = None
    ) -> Dict[str, Any]:
        """
        Builds the resolution context.
        options: dict containing 'env', 'config', 'app', 'state', 'request'
        extenders: list of async functions to extend context
        """
        request = options.get("request")
        
        base_context = {
            "env": options.get("env", dict(os.environ)),
            "config": options.get("config", {}),
            "app": options.get("app", {}),
            "state": options.get("state", {}),
            "request": request,
        }
        
        context = base_context.copy()
        
        if extenders:
            for extender in extenders:
                partial = await extender(context, request)
                context.update(partial)
                
        return context
