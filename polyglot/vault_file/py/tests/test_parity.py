import pytest
import json
from vault_file.core import to_json, from_json
from vault_file.domain import VaultFile, VaultHeader

def test_version_normalization():
    json_str = '{"header": {"version": "1.0", "created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {}}'
    loaded = from_json(json_str)
    assert loaded.header.version == "1.0.0"

def test_serialization_snake_case():
    file = VaultFile(
        header=VaultHeader(version="1.0.0", created_at="2023-01-01T00:00:00.000Z"),
        secrets={"MY_SECRET": "value"}
    )
    json_str = to_json(file)
    parsed = json.loads(json_str)
    assert "created_at" in parsed["header"]
