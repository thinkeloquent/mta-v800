from typing import TypeVar, Generic, Optional, List, Dict, Protocol, Any
from pydantic import BaseModel, Field
from .domain import LoadResult

T = TypeVar('T')

class SDKError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class SDKResult(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[SDKError] = None

class ConfigDescription(BaseModel):
    version: str
    vars_count: int
    sources: List[str]

class SecretInfo(BaseModel):
    key: str
    masked: str
    exists: bool

class ValidationResult(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]

class DiagnosticResult(BaseModel):
    initialized: bool
    vars_loaded: int
    issues: List[str]

class VaultFileSDKProtocol(Protocol):
    # CLI Operations
    def load_from_path(self, path: str) -> "SDKResult[LoadResult]": ...
    def validate_file(self, path: str) -> "SDKResult[ValidationResult]": ...
    def export_to_format(self, format: str, path: str) -> "SDKResult[None]": ...

    # Agent Operations
    def describe_config(self) -> "SDKResult[ConfigDescription]": ...
    def get_secret_safe(self, key: str) -> "SDKResult[SecretInfo]": ...
    def list_available_keys(self) -> "SDKResult[List[str]]": ...

    # DEV Tool Operations
    def diagnose_env_store(self) -> "SDKResult[DiagnosticResult]": ...
    def find_missing_required(self, keys: List[str]) -> "SDKResult[List[str]]": ...
    def suggest_missing_keys(self, partial: str) -> "SDKResult[List[str]]": ...
