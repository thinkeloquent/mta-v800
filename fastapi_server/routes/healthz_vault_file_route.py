from fastapi import FastAPI
from vault_file import EnvStore


def mount(app: FastAPI):
    """
    Mount vault-file health check routes to the FastAPI application.
    This function is called by the server bootstrap process.
    """

    @app.get("/healthz/admin/vault-file/status")
    async def vault_file_status():
        """Return the initialization status of the vault file EnvStore."""
        instance = EnvStore.get_instance()
        return {
            "initialized": EnvStore.is_initialized(),
            "total_vars_loaded": instance._total_vars_loaded,
        }

    @app.get("/healthz/admin/vault-file/json")
    async def vault_file_json():
        """Return the loaded vault file variables as JSON for debugging."""
        instance = EnvStore.get_instance()
        return {
            "initialized": EnvStore.is_initialized(),
            "total_vars_loaded": instance._total_vars_loaded,
            "store": dict(instance.store),
        }

    @app.get("/healthz/admin/vault-file/keys")
    async def vault_file_keys():
        """Return only the keys loaded from the vault file (no values)."""
        instance = EnvStore.get_instance()
        return {
            "initialized": EnvStore.is_initialized(),
            "total_vars_loaded": instance._total_vars_loaded,
            "keys": list(instance.store.keys()),
        }
