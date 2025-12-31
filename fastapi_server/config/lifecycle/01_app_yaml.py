from fastapi import FastAPI
from app_yaml_static_config import AppYamlConfig, AppYamlConfigSDK
from app_yaml_static_config.types import InitOptions
import os

async def onStartup(app: FastAPI, config: dict):
    print("Initializing App Yaml Static Config...")
    
    # Determine config directory relative to where config files should be
    # For this example, let's assume a 'config' folder at root, which is parent of this lifecycle folder's parent
    # But usually configured via env var or passed in config
    
    config_dir = os.getenv('CONFIG_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'common', 'config'))
    env = os.getenv('APP_ENV', 'dev').lower()  # Normalize to lowercase

    # Ensure config dir exists or fail gracefully/log
    if not os.path.exists(config_dir):
         print(f"Warning: Config dir {config_dir} not found, using defaults")

    options = InitOptions(
        files=[
            os.path.join(config_dir, 'base.yml'),
            os.path.join(config_dir, f'server.{env}.yaml')
        ],
        config_dir=config_dir
    )
    
    AppYamlConfig.initialize(options)
    app_config = AppYamlConfig.get_instance()

    app.state.config = app_config
    app.state.sdk = AppYamlConfigSDK(app_config)

    print(f"App Yaml Config loaded: {app.state.sdk.list_providers()}")
