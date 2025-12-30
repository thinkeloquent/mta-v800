import json
import os
from typing import Dict, Any
from .domain import VaultFile

def normalize_version(version: str) -> str:
    parts = version.split('.')
    while len(parts) < 3:
        parts.append('0')
    return '.'.join(parts[:3])

def to_json(vault_file: VaultFile) -> str:
    # Python internal is snake_case, JSON should be snake_case.
    # Pydantic defaults to snake_case for fields.
    return vault_file.model_dump_json(indent=2)

def from_json(json_str: str) -> VaultFile:
    data = json.loads(json_str)
    # Normalize version if present in header
    if 'header' in data and 'version' in data['header']:
        data['header']['version'] = normalize_version(data['header']['version'])
    return VaultFile.model_validate(data)

def parse_env_file(file_path: str) -> Dict[str, str]:
    if not os.path.exists(file_path):
        return {}
    
    env_vars = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                env_vars[key] = value
    return env_vars
