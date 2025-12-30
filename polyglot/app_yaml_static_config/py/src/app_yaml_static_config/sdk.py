from typing import Any, Dict, List, Optional
import json
import glob
import os
from .core import AppYamlConfig
from .types import InitOptions

class AppYamlConfigSDK:
    def __init__(self, config: AppYamlConfig):
        self.config = config

    @classmethod
    def from_directory(cls, config_dir: str) -> 'AppYamlConfigSDK':
        # Simple implementation assuming .yaml files in dir
        files = glob.glob(os.path.join(config_dir, "*.yaml"))
        AppYamlConfig.initialize(InitOptions(files=files, config_dir=config_dir))
        return cls(AppYamlConfig.get_instance())

    def get(self, key: str) -> Any:
        return json.loads(json.dumps(self.config.get(key)))

    def get_nested(self, keys: List[str]) -> Any:
         return json.loads(json.dumps(self.config.get_nested(*keys)))

    def get_all(self) -> Dict[str, Any]:
        return json.loads(json.dumps(self.config.get_all()))

    def list_providers(self) -> List[str]:
        providers = self.config.get('providers', {})
        return list(providers.keys())

    def list_services(self) -> List[str]:
         services = self.config.get('services', {})
         return list(services.keys())
    
    def list_storages(self) -> List[str]:
        storages = self.config.get('storages', {})
        return list(storages.keys())
