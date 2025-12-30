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
        self.logger: IVaultFileLogger = get_logger()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EnvStore()
        return cls._instance

    @classmethod
    def on_startup(cls, env_file: str = ".env", logger: Optional[IVaultFileLogger] = None) -> LoadResult:
        instance = cls.get_instance()
        if logger:
            instance.logger = logger
        elif instance.logger == get_logger():
             # Create default contextual logger if still using global default
             instance.logger = Logger.create("vault_file", "env_store")
             
        instance.logger.info(f"Starting EnvStore initialization from {env_file}...")
        instance._initialized = True
        
        if os.path.exists(env_file):
            instance.logger.debug(f"Found env file at {env_file}, parsing...")
            file_vars = parse_env_file(env_file)
            count = len(file_vars)
            instance.logger.debug(f"Parsed {count} variables from file.")
            
            for key, value in file_vars.items():
                instance.store[key] = value
        else:
            instance.logger.warn(f"Env file not found at {env_file}")
                
        instance._total_vars_loaded = len(os.environ) + len(instance.store)
        instance.logger.info(f"EnvStore initialized. Total accessible vars (approx): {instance._total_vars_loaded}")
        return LoadResult(totalVarsLoaded=instance._total_vars_loaded)

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        instance = cls.get_instance()
        # Python Priority: Internal Store > System Environment
        if key in instance.store:
            return instance.store[key]
        if key in os.environ:
            return os.environ[key]
        
        instance.logger.debug(f"Env var '{key}' not found, using default: {default}")
        return default

    @classmethod
    def get_or_throw(cls, key: str) -> str:
        value = cls.get(key)
        if value is None:
            instance = cls.get_instance()
            instance.logger.error(f"Required env var '{key}' missing.")
            raise EnvKeyNotFoundError(key)
        return value

    @classmethod
    def is_initialized(cls) -> bool:
        return cls.get_instance()._initialized

