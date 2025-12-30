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
        self.logger: IVaultFileLogger = Logger.create("vault_file", "sdk.py")
        self.logger.debug("VaultFileSDK instance created")

    @classmethod
    def create(cls) -> "VaultFileSDKBuilder":
        return VaultFileSDKBuilder()

    def set_env_path(self, path: str):
        self.logger.debug(f"set_env_path() called: {path}")
        self.env_path = path

    def set_base64_parsers(self, parsers: Dict[str, Callable[[str], Any]]):
        self.logger.debug(f"set_base64_parsers() called with {len(parsers)} parsers")
        self.base64_parsers = parsers

    def set_logger(self, logger: IVaultFileLogger):
        self.logger.debug("Custom logger being injected")
        self.logger = logger

    def _success(self, data: Optional[Any] = None) -> SDKResult:
        return SDKResult(success=True, data=data)

    def _failure(self, message: str, code: str = "UNKNOWN_ERROR", details: Optional[Dict] = None) -> SDKResult:
        self.logger.error(f"SDK operation failed: [{code}] {message}", details if details else {})
        return SDKResult(success=False, error=SDKError(code=code, message=message, details=details))

    # CLI Operations
    def load_config(self) -> SDKResult[LoadResult]:
        self.logger.info(f"load_config() called, env_path={self.env_path}")
        try:
            result = EnvStore.on_startup(self.env_path, self.logger)
            self.logger.info(f"load_config() succeeded: total_vars_loaded={result.totalVarsLoaded}")
            return self._success(result)
        except Exception as e:
            self.logger.error(f"load_config() failed: {e}")
            return self._failure(str(e), "LOAD_ERROR")

    def load_from_path(self, path: str) -> SDKResult[LoadResult]:
        self.logger.info(f"load_from_path() called: {path}")

        if not path:
            self.logger.error("load_from_path() called with empty path")
            return self._failure("File path is required", "INVALID_ARGUMENT")

        try:
            if not os.path.exists(path):
                self.logger.warn(f"load_from_path() file not found: {path}")
                return self._failure(f"File not found: {path}", "FILE_NOT_FOUND")

            self.logger.debug(f"Parsing env file: {path}")
            vars_dict = parse_env_file(path)
            count = len(vars_dict)
            self.logger.info(f"load_from_path() succeeded: {path}, total_vars_loaded={count}")
            return self._success(LoadResult(totalVarsLoaded=count))
        except Exception as e:
            self.logger.error(f"load_from_path() failed: {path}, error={e}")
            return self._failure(str(e), "LOAD_ERROR")

    def validate_file(self, path: str) -> SDKResult[ValidationResult]:
        self.logger.info(f"validate_file() called: {path}")

        if not path:
            self.logger.error("validate_file() called with empty path")
            return self._failure("File path is required", "INVALID_ARGUMENT")

        if not os.path.exists(path):
            self.logger.warn(f"validate_file() file not found: {path}")
            return self._failure(f"File not found: {path}", "FILE_NOT_FOUND")

        try:
            self.logger.debug(f"Attempting to parse file for validation: {path}")
            parse_env_file(path)
            self.logger.info(f"validate_file() succeeded - file is valid: {path}")
            return self._success(ValidationResult(valid=True, errors=[], warnings=[]))
        except Exception as e:
            self.logger.warn(f"validate_file() found invalid file: {path}, error={e}")
            return self._success(ValidationResult(valid=False, errors=[str(e)], warnings=[]))

    def export_to_format(self, format: str, path: str) -> SDKResult[None]:
        self.logger.info(f"export_to_format() called: format={format}, path={path}")
        self.logger.warn("export_to_format() not implemented")
        return self._failure("Not implemented", "NOT_IMPLEMENTED")

    # Agent Operations
    def describe_config(self) -> SDKResult[ConfigDescription]:
        self.logger.debug("describe_config() called")
        instance = EnvStore.get_instance()
        vars_count = instance._total_vars_loaded
        self.logger.debug(f"describe_config() returning: vars_count={vars_count}, sources=[{self.env_path}]")
        return self._success(ConfigDescription(
            version="1.0.0",
            vars_count=vars_count,
            sources=[self.env_path]
        ))

    def get_secret_safe(self, key: str) -> SDKResult[SecretInfo]:
        self.logger.debug(f"get_secret_safe() called: key={key}")
        if not key:
            self.logger.warn("get_secret_safe() called with empty key")
        val = EnvStore.get(key)
        exists = val is not None
        self.logger.debug(f"get_secret_safe() result: key={key}, exists={exists}")
        return self._success(SecretInfo(
            key=key,
            masked="***" if exists else "",
            exists=exists
        ))

    def list_available_keys(self) -> SDKResult[List[str]]:
        self.logger.debug("list_available_keys() called")
        self.logger.warn("list_available_keys() not fully implemented - returning empty list")
        return self._success([])

    # DEV Tool Operations
    def diagnose_env_store(self) -> SDKResult[DiagnosticResult]:
        self.logger.debug("diagnose_env_store() called")
        initialized = EnvStore.is_initialized()
        self.logger.info(f"diagnose_env_store() result: initialized={initialized}")
        return self._success(DiagnosticResult(
            initialized=initialized,
            vars_loaded=0,
            issues=[]
        ))

    def find_missing_required(self, keys: List[str]) -> SDKResult[List[str]]:
        self.logger.info(f"find_missing_required() called: keys_count={len(keys) if keys else 0}")
        if not keys:
            self.logger.debug("find_missing_required() no keys to check")
            return self._success([])

        missing = [k for k in keys if EnvStore.get(k) is None]
        if missing:
            self.logger.warn(f"find_missing_required() FOUND MISSING KEYS: {', '.join(missing)}")
        else:
            self.logger.debug("find_missing_required() all keys present")
        return self._success(missing)

    def suggest_missing_keys(self, partial: str) -> SDKResult[List[str]]:
        self.logger.debug(f"suggest_missing_keys() called: partial={partial}")
        self.logger.warn("suggest_missing_keys() not implemented - returning empty list")
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

