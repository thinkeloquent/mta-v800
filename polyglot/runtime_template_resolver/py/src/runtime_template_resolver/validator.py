import re
from .errors import ValidationError

def validate_placeholder(placeholder: str) -> None:
    if not placeholder or not placeholder.strip():
        raise ValidationError("Placeholder cannot be empty")
    
    # Basic validation
    if not re.match(r'^[\w\-\.\[\]"\']+$', placeholder):
        raise ValidationError(f"Invalid characters in placeholder: {placeholder}")

    if ".." in placeholder:
        raise ValidationError(f"Invalid path (empty segment): {placeholder}")
