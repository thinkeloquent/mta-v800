from vault_file import EnvStore
import os

# EnvStore logic to load from VAULT_SECRET_FILE if present
def load_env_vars():
    # This logic runs when the module is imported by the server bootstrap
    print(f"Loading Vault File integration... {os.environ.get("VAULT_SECRET_FILE", ".env")}")
    # The integration docs say:
    # server: config.bootstrap.load_env = "{serverPath}/config/env" => load files in order
    
    # We can rely on EnvStore.on_startup() to check VAULT_SECRET_FILE env var
    # Or explicitly pass it if we have it from another source.
    # The requirement says:
    # envFile will be an ENV variable `VAULT_SECRET_FILE`
    
    result = EnvStore.on_startup(os.environ.get("VAULT_SECRET_FILE", ".env"))
    print(f"Vault File loaded: {result.total_vars_loaded} vars")

load_env_vars()
