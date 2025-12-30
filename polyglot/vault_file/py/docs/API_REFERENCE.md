# Python API Reference

## Core Components

### EnvStore
Singleton for managing environment variables.

```python
class EnvStore:
    @classmethod
    def on_startup(cls, env_file: str = ".env", logger: Optional[IVaultFileLogger] = None) -> LoadResult:
        """
        Startup hook to load environment variables.
        Priority: Internal Store > os.environ
        """
        ...

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get value from store."""
        ...

    @classmethod
    def get_or_throw(cls, key: str) -> str:
        """Get value or throw if missing."""
        ...

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if on_startup has been called."""
        ...
```

## SDK

### VaultFileSDK
High-level SDK for interacting with Vault File.

```python
sdk = (VaultFileSDK.create()
    .with_env_path('.env')
    .with_logger(custom_logger)
    .build())
```

#### Builder Methods
*   `with_env_path(path: str) -> VaultFileSDKBuilder` - Set path to .env file
*   `with_base64_parsers(parsers: Dict) -> VaultFileSDKBuilder` - Set custom parsers
*   `with_logger(logger: IVaultFileLogger) -> VaultFileSDKBuilder` - Set custom logger

#### Operations
*   `load_config() -> SDKResult[LoadResult]` - Load configuration
*   `load_from_path(path: str) -> SDKResult[LoadResult]` - Load from specific path
*   `validate_file(path: str) -> SDKResult[ValidationResult]` - Validate file integrity
*   `describe_config() -> SDKResult[ConfigDescription]` - Get config metadata
*   `get_secret_safe(key: str) -> SDKResult[SecretInfo]` - Get masked secret
