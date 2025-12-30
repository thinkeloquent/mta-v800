import json
import os
from typing import Dict, Any
from .domain import VaultFile
from .logger import Logger, IVaultFileLogger

log: IVaultFileLogger = Logger.create("vault_file", "core.py")


def normalize_version(version: str) -> str:
    parts = version.split('.')
    while len(parts) < 3:
        parts.append('0')
    return '.'.join(parts[:3])


def to_json(vault_file: VaultFile) -> str:
    log.debug("Converting VaultFile to JSON")
    try:
        result = vault_file.model_dump_json(indent=2)
        log.debug(f"Successfully converted VaultFile to JSON, length={len(result)}")
        return result
    except Exception as e:
        log.error(f"Failed to convert VaultFile to JSON: {e}")
        raise


def from_json(json_str: str) -> VaultFile:
    log.debug(f"Parsing JSON to VaultFile, input_length={len(json_str) if json_str else 0}")

    if not json_str or not isinstance(json_str, str):
        log.error("Invalid JSON input: input is empty or not a string")
        raise ValueError("Invalid JSON input: input is empty or not a string")

    try:
        data = json.loads(json_str)
        log.debug("JSON parsed successfully")

        # Normalize version if present in header
        if 'header' in data and 'version' in data['header']:
            original_version = data['header']['version']
            data['header']['version'] = normalize_version(data['header']['version'])
            log.debug(f"Normalized version from '{original_version}' to '{data['header']['version']}'")

        result = VaultFile.model_validate(data)
        log.debug("Successfully parsed JSON to VaultFile structure")
        return result
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse JSON: {e}")
        raise
    except Exception as e:
        log.error(f"Failed to validate VaultFile structure: {e}")
        raise


def parse_env_file(file_path: str) -> Dict[str, str]:
    log.debug(f"Attempting to parse env file: {file_path}")

    if not file_path:
        log.error("parse_env_file called with empty or None file_path")
        raise ValueError("File path is required")

    if not os.path.exists(file_path):
        log.warn(f"Env file not found, returning empty dict: {file_path}")
        return {}

    log.info(f"Loading env file: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        log.debug(f"File read successfully: {file_path}, content_length={len(content)}")
    except IOError as e:
        log.error(f"Failed to read env file: {file_path}, error={e}")
        raise

    if not content or not content.strip():
        log.warn(f"Env file is empty: {file_path}")
        return {}

    env_vars: Dict[str, str] = {}
    lines = content.split('\n')
    line_number = 0
    parsed_count = 0
    skipped_count = 0
    error_count = 0

    for line in lines:
        line_number += 1
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            skipped_count += 1
            continue

        if '=' not in line:
            log.warn(f"Skipping malformed line (no '=' found): {file_path}:{line_number} -> '{line}'")
            error_count += 1
            continue

        key, value = line.split('=', 1)
        key = key.strip()

        if not key:
            log.warn(f"Skipping line with empty key: {file_path}:{line_number} -> '{line}'")
            error_count += 1
            continue

        value = value.strip()

        # Remove quotes if present
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]

        env_vars[key] = value
        parsed_count += 1
        log.debug(f"Parsed env var: key={key}, line={line_number}")

    log.info(f"Finished parsing env file: {file_path}, "
             f"total_lines={line_number}, parsed_vars={parsed_count}, "
             f"skipped_lines={skipped_count}, malformed_lines={error_count}")

    if error_count > 0:
        log.warn(f"Some lines could not be parsed: {file_path}, malformed_lines={error_count}")

    return env_vars
