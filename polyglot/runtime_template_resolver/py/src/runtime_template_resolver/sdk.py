from typing import List, Any, Dict, Optional
from .resolver import TemplateResolver
from .interfaces import ResolverOptions
from .validator import validate_placeholder
from .extractor import extract_placeholders
from .compiler import compile as compile_template

_default_resolver = TemplateResolver()

def resolve(template: str, context: Dict[str, Any], options: Optional[ResolverOptions] = None) -> str:
    return _default_resolver.resolve(template, context, options)

def resolve_many(templates: List[str], context: Dict[str, Any], options: Optional[ResolverOptions] = None) -> List[str]:
    return [_default_resolver.resolve(t, context, options) for t in templates]

def resolve_object(obj: Any, context: Dict[str, Any], options: Optional[ResolverOptions] = None) -> Any:
    return _default_resolver.resolve_object(obj, context, options)

def validate(template: str) -> None:
    placeholders = extract_placeholders(template)
    for p in placeholders:
        key = p
        if "|" in p:
            key = p.split("|")[0]
        validate_placeholder(key.strip())

def extract(template: str) -> List[str]:
    return extract_placeholders(template)

def compile(template: str):
    return compile_template(template)
