import os
from typing import Optional, Dict, List, Any
from app_yaml_static_config import AppYamlConfig
# Depending on runtime_template_resolver being available
try:
    from runtime_template_resolver import create_resolver, ComputeScope
except ImportError:
    # Defining mock for fallback/scaffold
    create_resolver = None
    class ComputeScope:
        STARTUP = "STARTUP"
        REQUEST = "REQUEST"

from .logger import Logger
from .context_builder import ContextBuilder, ContextExtender
from .overwrite_merger import apply_overwrites

class ConfigSDK:
    _instance = None

    def __init__(self, options: Dict[str, Any] = None):
        options = options or {}
        self.logger = Logger.create('config-sdk', 'sdk.py')
        self.context_extenders: List[ContextExtender] = options.get('context_extenders', [])
        self.raw_config: Dict[str, Any] = {}
        self.initialized = False
        self.registry = None

    @classmethod
    async def initialize(cls, options: Dict[str, Any] = None) -> 'ConfigSDK':
        """
        Async initialization of the ConfigSDK.
        """
        if cls._instance:
            return cls._instance
            
        sdk = cls(options)
        await sdk._bootstrap(options)
        cls._instance = sdk
        return sdk

    @classmethod
    def get_instance(cls) -> 'ConfigSDK':
        if not cls._instance:
            raise RuntimeError("ConfigSDK not initialized. Call initialize() first.")
        return cls._instance

    async def _bootstrap(self, options: Dict[str, Any]):
        self.logger.debug("Bootstrapping ConfigSDK...")
        
        # 1. Load Static Config
        instance = AppYamlConfig.get_instance()
        self.raw_config = instance.get_all()
        self.logger.debug("Raw config loaded", data={"keys": list(self.raw_config.keys())})
        
        # 2. Setup Registry (Mock/Placeholder or Load)
        # Assuming registry is available. In integration, we should probably
        # allow parsing it or it auto-loads from environment.
        class MockRegistry:
            def list(self): return []
            
        self.registry = MockRegistry()
        self.initialized = True

    def get_raw(self) -> Dict[str, Any]:
        return self.raw_config

    async def get_resolved(self, scope: str, request: Any = None) -> Dict[str, Any]:
        if not self.initialized:
            raise RuntimeError("SDK not initialized")

        context = await ContextBuilder.build({
            "config": self.raw_config,
            "app": self.raw_config.get("app", {}),
            "request": request
        }, self.context_extenders)

        if not create_resolver:
             self.logger.warn("runtime_template_resolver not found, returning raw config")
             return self.raw_config

        resolver = create_resolver(self.registry)
        resolved = await resolver.resolve_object(
            self.raw_config,
            context=context,
            scope=scope
        )
        
        # Merge overwrites logic if separate
        # resolved = apply_overwrites(resolved, resolved.get("overwrite_from_context", {}))
        
        return resolved

    async def to_json(self, options: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.get_raw()
