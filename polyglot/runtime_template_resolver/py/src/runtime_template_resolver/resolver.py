import re
from typing import Any, Dict, Optional, List
from .logger import logger
from .interfaces import ResolverOptions, MissingStrategy, TemplateResolverProtocol
from .errors import SecurityError
from .path_parser import parse_path
from .validator import validate_placeholder
from .coercion import to_string
from .missing_handler import handle_missing
from .batch import resolve_object as batch_resolve_object

log = logger.create("runtime_template_resolver", __file__)

class TemplateResolver:
    def resolve(self, template: str, context: Dict[str, Any], options: Optional[ResolverOptions] = None) -> str:
        log.debug("resolve() called", template_length=len(template))
        effective_log = options.logger if options and options.logger else log
        missing_strategy = options.missing_strategy if options and options.missing_strategy else MissingStrategy.EMPTY
        throw_on_error = options.throw_on_error if options and options.throw_on_error else False

        def replacer(match):
            inner = match.group(1)
            raw_inner = inner.strip()
            key = raw_inner
            default_value = None

            if "|" in key:
                parts = key.split("|")
                key = parts[0].strip()
                default_part = "|".join(parts[1:]).strip()
                if (default_part.startswith('"') and default_part.endswith('"')) or \
                   (default_part.startswith("'") and default_part.endswith("'")):
                    default_value = default_part[1:-1]
                else:
                    default_value = default_part

            try:
                validate_placeholder(key)
                segments = parse_path(key)
                current = context

                for segment in segments:
                    if segment.startswith('_'):
                        msg = f"Access to private/unsafe attribute '{segment}' is denied"
                        effective_log.warning(msg, segment=segment)
                        raise SecurityError(msg)
                    
                    if current is None:
                        current = None
                        break
                    
                    if isinstance(current, (dict, list)):
                        if isinstance(current, list):
                            if segment.isdigit():
                                idx = int(segment)
                                if 0 <= idx < len(current):
                                    current = current[idx]
                                else:
                                    current = None
                            else:
                                current = None
                        else:
                            # dict
                             current = current.get(segment)
                    else:
                        if hasattr(current, segment):
                             current = getattr(current, segment)
                        else:
                             current = None
                             break

                if current is None:
                    if default_value is not None:
                        return default_value
                    return handle_missing(key, missing_strategy, default_value)
                
                return to_string(current)

            except Exception as err:
                effective_log.error(str(err), key=raw_inner)
                if throw_on_error:
                    raise err
                return match.group(0)

        return re.sub(r"{{([^}]+)}}", replacer, template)

    def resolve_object(self, obj: Any, context: Dict[str, Any], options: Optional[ResolverOptions] = None) -> Any:
        return batch_resolve_object(obj, context, self, options)
