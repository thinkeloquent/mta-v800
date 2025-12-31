from typing import Callable, Any, Dict
from .logger import logger
from .resolver import TemplateResolver

log = logger.create("runtime_template_resolver", __file__)
_resolver = TemplateResolver()

def compile(template: str) -> Callable[[Dict[str, Any]], str]:
    log.debug("Compiling template", template=template)
    def compiled(context: Dict[str, Any]) -> str:
        return _resolver.resolve(template, context)
    return compiled
