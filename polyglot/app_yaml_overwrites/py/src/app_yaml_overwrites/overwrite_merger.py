
from typing import Dict, Any

def apply_overwrites(original_config: Dict[str, Any], overwrite_section: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merges overwrite_section into original_config.
    """
    if not overwrite_section:
        return original_config

    result = original_config.copy()
    
    for key, value in overwrite_section.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = apply_overwrites(result[key], value)
        else:
            result[key] = value
            
    return result
