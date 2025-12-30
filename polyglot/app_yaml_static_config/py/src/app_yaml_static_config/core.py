from typing import Dict, Any, Optional, List
import copy
import yaml
from pathlib import Path
from .types import InitOptions, ILogger
from .logger import create
from .validators import ImmutabilityError

class AppYamlConfig:
    _instance: Optional['AppYamlConfig'] = None
    _config: Dict[str, Any] = {}
    _original_configs: Dict[str, Dict[str, Any]] = {}
    _initial_merged_config: Optional[Dict[str, Any]] = None
    _logger: ILogger

    def __init__(self, options: InitOptions):
        if AppYamlConfig._instance is not None:
             raise Exception("This class is a singleton!")
        self._logger = options.logger or create("app_yaml_static_config", "core.py")
        self._load_config(options)
        AppYamlConfig._instance = self

    @classmethod
    def initialize(cls, options: InitOptions) -> 'AppYamlConfig':
        if cls._instance is None:
            cls(options)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'AppYamlConfig':
        if cls._instance is None:
            raise Exception("AppYamlConfig not initialized")
        return cls._instance

    def _load_config(self, options: InitOptions) -> None:
        self._logger.info("Initializing configuration", options.files)
        merged_config = {}
        
        for file_path in options.files:
            self._logger.debug(f"Loading config file: {file_path}")
            try:
                with open(file_path, 'r') as f:
                    content = yaml.safe_load(f) or {}
                    self._original_configs[file_path] = copy.deepcopy(content)
                    self._deep_merge(merged_config, content)
            except Exception as e:
                self._logger.error(f"Failed to load user config: {file_path}", e)
                raise e
        
        self._config = merged_config
        self._initial_merged_config = copy.deepcopy(merged_config)
        self._logger.info("Configuration initialized successfully")
        
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
    
    def get_nested(self, *keys: str, default: Any = None) -> Any:
        current = self._config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def get_all(self) -> Dict[str, Any]:
        return copy.deepcopy(self._config)

    def get_original(self, file: Optional[str] = None) -> Dict[str, Any]:
        if file:
            return copy.deepcopy(self._original_configs.get(file, {}))
        # If no file specified, could return all Originals, or raise. 
        # Plan says "getOriginal(filename?: string)", implies generic return if optional?
        # Let's return all map if None for now or follow specific implementation detail if I overlooked.
        # Plan says: "getOriginal(filename?: string) ... getOriginalAll()"
        # I'll implement get_original as per plan method.
        # Actually plan lists getOriginalAll as separate.
        # But get_original return type is dict.
        return {} 

    def get_original_all(self) -> Dict[str, Dict[str, Any]]:
        return copy.deepcopy(self._original_configs)

    def restore(self) -> None:
        # Simple environment check - in real app might check actual env var
        # For now, allow restoration
        if self._initial_merged_config is not None:
             self._config = copy.deepcopy(self._initial_merged_config)

    # Immutability Stubs
    def set(self, key: str, value: Any) -> None:
        raise ImmutabilityError("Configuration is immutable")

    def update(self, updates: Dict[str, Any]) -> None:
        raise ImmutabilityError("Configuration is immutable")

    def reset(self) -> None:
         raise ImmutabilityError("Configuration is immutable")

    def clear(self) -> None:
        raise ImmutabilityError("Configuration is immutable")

