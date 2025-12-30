import os
from typing import Dict, Optional, Any
from .domain import LoadResult
from .core import parse_env_file
from .validators import EnvKeyNotFoundError
from .logger import IVaultFileLogger, get_logger, Logger

class EnvStore:
    _instance = None

    def __init__(self):
        self.store: Dict[str, str] = {}
        self._initialized = False
        self._total_vars_loaded = 0
        self.logger: IVaultFileLogger = Logger.create("vault_file", "env_store.py")
        self.logger.debug("EnvStore instance created")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EnvStore()
            cls._instance.logger.debug("EnvStore singleton initialized")
        return cls._instance

    @classmethod
    def on_startup(cls, env_file: str = ".env", logger: Optional[IVaultFileLogger] = None) -> LoadResult:
        instance = cls.get_instance()
        if logger:
            instance.logger = logger
            instance.logger.debug("Custom logger injected into EnvStore")

        instance.logger.info("=== EnvStore Startup Begin ===")
        instance.logger.info(f"on_startup() called: env_file={env_file}")

        if not env_file:
            instance.logger.error("on_startup() called with empty env_file path")
            raise ValueError("Environment file path is required")

        instance._initialized = True
        instance.logger.debug("EnvStore marked as initialized")

        if os.path.exists(env_file):
            instance.logger.info(f"Env file found: {env_file}")

            try:
                file_vars = parse_env_file(env_file)
                count = len(file_vars)

                if count == 0:
                    instance.logger.warn(f"Env file exists but contains no variables: {env_file}")
                else:
                    instance.logger.info(f"Successfully parsed env file: {env_file}, variable_count={count}")

                    for key, value in file_vars.items():
                        instance.store[key] = value
                        instance.logger.debug(f"Loaded env var into store: key={key}")
            except Exception as e:
                instance.logger.error(f"Failed to parse env file: {env_file}, error={e}")
                raise
        else:
            instance.logger.warn(f"Env file NOT FOUND - this may cause missing configuration: {env_file}")
            abs_path = os.path.abspath(env_file)
            instance.logger.warn(f"Expected file location: {abs_path}")

        process_env_count = len(os.environ)
        store_count = len(instance.store)
        instance._total_vars_loaded = process_env_count + store_count

        instance.logger.info("=== EnvStore Startup Complete ===")
        instance.logger.info(f"process_env_vars={process_env_count}, file_vars={store_count}, total_accessible={instance._total_vars_loaded}")

        return LoadResult(totalVarsLoaded=instance._total_vars_loaded)

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        instance = cls.get_instance()

        if not key:
            instance.logger.warn("get() called with empty key")
            return default

        # Python Priority: Internal Store > System Environment
        if key in instance.store:
            instance.logger.debug(f"Env var found in internal store: key={key}")
            return instance.store[key]

        if key in os.environ:
            instance.logger.debug(f"Env var found in os.environ: key={key}")
            return os.environ[key]

        if default is not None:
            instance.logger.debug(f"Env var not found, using default: key={key}, has_default=True")
        else:
            instance.logger.debug(f"Env var not found, no default provided: key={key}")

        return default

    @classmethod
    def get_or_throw(cls, key: str) -> str:
        instance = cls.get_instance()

        if not key:
            instance.logger.error("get_or_throw() called with empty key")
            raise ValueError("Key is required")

        instance.logger.debug(f"get_or_throw() called: key={key}")

        value = cls.get(key)
        if value is None:
            instance.logger.error(f"REQUIRED ENV VAR MISSING: key={key}")
            instance.logger.error(f"Hint: Please ensure '{key}' is set in your .env file or environment")
            raise EnvKeyNotFoundError(key)

        instance.logger.debug(f"get_or_throw() succeeded: key={key}")
        return value

    @classmethod
    def is_initialized(cls) -> bool:
        initialized = cls.get_instance()._initialized
        cls.get_instance().logger.debug(f"is_initialized() called: initialized={initialized}")
        return initialized

