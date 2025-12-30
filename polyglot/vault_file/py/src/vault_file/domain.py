from datetime import datetime, timezone
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator
import re

class VaultHeader(BaseModel):
    version: str = Field(default="1.0.0", description="Semantic version of the vault file")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec='milliseconds'), description="ISO 8601 timestamp")
    description: Optional[str] = None

    @field_validator('version')
    def validate_version(cls, v):
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError("Version must be semantic versioning (x.y.z)")
        return v

class VaultFile(BaseModel):
    header: VaultHeader
    secrets: Dict[str, str]

class LoadResult(BaseModel):
    total_vars_loaded: int = Field(alias="totalVarsLoaded")
