from fastapi import FastAPI
from app_yaml_static_config import AppYamlConfig, AppYamlConfigSDK


def mount(app: FastAPI):
    """
    Mount app-yaml-static-config health check routes to the FastAPI application.
    This function is called by the server bootstrap process.
    """

    @app.get("/healthz/admin/app-yaml-static-config/status")
    async def app_yaml_config_status():
        """Return the initialization status of the app yaml config."""
        try:
            instance = AppYamlConfig.get_instance()
            sdk = AppYamlConfigSDK(instance)
            return {
                "initialized": True,
                "providers": sdk.list_providers(),
                "services": sdk.list_services(),
                "storages": sdk.list_storages(),
            }
        except Exception as e:
            return {
                "initialized": False,
                "error": str(e),
            }

    @app.get("/healthz/admin/app-yaml-static-config/json")
    async def app_yaml_config_json():
        """Return the full merged configuration as JSON for debugging."""
        try:
            instance = AppYamlConfig.get_instance()
            sdk = AppYamlConfigSDK(instance)
            return {
                "initialized": True,
                "config": sdk.get_all(),
                "original_files": instance.get_original_all(),
            }
        except Exception as e:
            return {
                "initialized": False,
                "error": str(e),
            }

    @app.get("/healthz/admin/app-yaml-static-config/keys")
    async def app_yaml_config_keys():
        """Return only the top-level keys from the configuration (no values)."""
        try:
            instance = AppYamlConfig.get_instance()
            config = instance.get_all()
            original_files = instance.get_original_all()
            return {
                "initialized": True,
                "top_level_keys": list(config.keys()),
                "loaded_files": list(original_files.keys()),
            }
        except Exception as e:
            return {
                "initialized": False,
                "error": str(e),
            }
