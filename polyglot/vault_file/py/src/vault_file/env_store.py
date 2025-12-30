import os
from typing import Dict, Optional
from .domain import LoadResult
from .core import parse_env_file
from .validators import EnvKeyNotFoundError

class EnvStore:
    _instance = None
    
    def __init__(self):
        self.store: Dict[str, str] = {}
        self._initialized = False
        self._total_vars_loaded = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EnvStore()
        return cls._instance

    @classmethod
    def on_startup(cls, env_file: str = ".env") -> LoadResult:
        instance = cls.get_instance()
        instance._initialized = True
        
        if os.path.exists(env_file):
            file_vars = parse_env_file(env_file)
            for key, value in file_vars.items():
                instance.store[key] = value
                
        instance._total_vars_loaded = len(os.environ) + len(instance.store)
        return LoadResult(totalVarsLoaded=instance._total_vars_loaded)

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        instance = cls.get_instance()
        # Python Priority: Internal Store > System Environment
        if key in instance.store:
            return instance.store[key]
        if key in os.environ:
            return os.environ[key]
        return default

    @classmethod
    def get_or_throw(cls, key: str) -> str:
        value = cls.get(key)
        if value is None:
            raise EnvKeyNotFoundError(key)
        return value

    @classmethod
    def is_initialized(cls) -> bool:
        return cls.get_instance()._initialized
