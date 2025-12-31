import re
from typing import List
from .logger import logger

log = logger.create("runtime_template_resolver", __file__)

def extract_placeholders(template: str) -> List[str]:
    log.debug("extract_placeholders() called", template=template)
    
    matches = re.findall(r"{{([^}]+)}}", template)
    if not matches:
        log.debug("No placeholders found")
        return []
        
    placeholders = [m.strip() for m in matches]
    log.debug("Placeholders extracted", count=len(placeholders), placeholders=placeholders)
    return placeholders
