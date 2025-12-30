import os
from typing import Dict, List, Optional, Any, Callable
from .domain import LoadResult
from .core import parse_env_file
from .env_store import EnvStore
from .sdk_types import (
    SDKResult, SDKError, ConfigDescription, SecretInfo,
    ValidationResult, DiagnosticResult, VaultFileSDKProtocol
)
from .logger import IVaultFileLogger, get_logger, Logger

class VaultFileSDK:
    def __init__(self):
        self.env_path: str = ".env"
        self.base64_parsers: Dict[str, Callable[[str], Any]] = {}
        self.logger: IVaultFileLogger = get_logger()

    @classmethod
    def create(cls) -> "VaultFileSDKBuilder":
        return VaultFileSDKBuilder()

    def set_env_path(self, path: str):
        self.env_path = path

    def set_base64_parsers(self, parsers: Dict[str, Callable[[str], Any]]):
        self.base64_parsers = parsers

    def set_logger(self, logger: IVaultFileLogger):
        self.logger = logger

    def _success(self, data: Optional[Any] = None) -> SDKResult:
        return SDKResult(success=True, data=data)

    def _failure(self, message: str, code: str = "UNKNOWN_ERROR", details: Optional[Dict] = None) -> SDKResult:
        self.logger.error(f"SDK Operation Failed: [{code}] {message}", details)
        return SDKResult(success=False, error=SDKError(code=code, message=message, details=details))

    # CLI Operations
    def load_config(self) -> SDKResult[LoadResult]:
        self.logger.info(f"Loading config from {self.env_path}")
        try:
            result = EnvStore.on_startup(self.env_path, self.logger)
            self.logger.info(f"Config loaded successfully: {result}")
            return self._success(result)
        except Exception as e:
            return self._failure(str(e), "LOAD_ERROR")

    def load_from_path(self, path: str) -> SDKResult[LoadResult]:
        self.logger.info(f"Loading from specific path: {path}")
        try:
            if not os.path.exists(path):
                return self._failure(f"File not found: {path}", "FILE_NOT_FOUND")
            
            vars_dict = parse_env_file(path)
            count = len(vars_dict)
            self.logger.debug(f"Parsed {count} vars from {path}")
            return self._success(LoadResult(totalVarsLoaded=count))
        except Exception as e:
            return self._failure(str(e), "LOAD_ERROR")

    def validate_file(self, path: str) -> SDKResult[ValidationResult]:
        self.logger.info(f"Validating file: {path}")
        if not os.path.exists(path):
            return self._failure(f"File not found: {path}", "FILE_NOT_FOUND")
        try:
            parse_env_file(path)
            self.logger.debug(f"File {path} is valid.")
            return self._success(ValidationResult(valid=True, errors=[], warnings=[]))
        except Exception as e:
            self.logger.warn(f"File {path} invalid: {e}")
            return self._success(ValidationResult(valid=False, errors=[str(e)], warnings=[]))

    def export_to_format(self, format: str, path: str) -> SDKResult[None]:
        return self._failure("Not implemented", "NOT_IMPLEMENTED")

    # Agent Operations
    def describe_config(self) -> SDKResult[ConfigDescription]:
        # Accessing private attribute strictly speaking, but okay for SDK impl within package
        instance = EnvStore.get_instance()
        return self._success(ConfigDescription(
            version="1.0.0",
            vars_count=instance._total_vars_loaded,
            sources=[self.env_path]
        ))

    def get_secret_safe(self, key: str) -> SDKResult[SecretInfo]:
        val = EnvStore.get(key)
        exists = val is not None
        return self._success(SecretInfo(
            key=key,
            masked="***" if exists else "",
            exists=exists
        ))

    def list_available_keys(self) -> SDKResult[List[str]]:
        return self._success([])

    # DEV Tool Operations
    def diagnose_env_store(self) -> SDKResult[DiagnosticResult]:
        return self._success(DiagnosticResult(
            initialized=EnvStore.is_initialized(),
            vars_loaded=0,
            issues=[]
        ))

    def find_missing_required(self, keys: List[str]) -> SDKResult[List[str]]:
        missing = [k for k in keys if EnvStore.get(k) is None]
        if missing:
             self.logger.warn(f"Missing required keys: {', '.join(missing)}")
        return self._success(missing)

    def suggest_missing_keys(self, partial: str) -> SDKResult[List[str]]:
        return self._success([])


class VaultFileSDKBuilder:
    def __init__(self):
        self.sdk = VaultFileSDK()

    def with_env_path(self, path: str) -> "VaultFileSDKBuilder":
        self.sdk.set_env_path(path)
        return self

    def with_base64_parsers(self, parsers: Dict[str, Callable[[str], Any]]) -> "VaultFileSDKBuilder":
        self.sdk.set_base64_parsers(parsers)
        return self

    def with_logger(self, logger: IVaultFileLogger) -> "VaultFileSDKBuilder":
        self.sdk.set_logger(logger)
        return self

    def build(self) -> VaultFileSDK:
        logger = self.sdk.logger
        if not logger or logger == get_logger():
             # Use factory if no specific logger provided
             self.sdk.set_logger(Logger.create("vault_file", "sdk"))
        return self.sdk

