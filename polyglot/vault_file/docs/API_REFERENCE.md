# Vault File API Reference

## Core Components

### VaultFile
The data container for configuration and secrets.

**TypeScript**
```typescript
interface IVaultFile {
  header: VaultHeader;
  secrets: Record<string, string>;
}
```

**Python**
```python
class VaultFile(BaseModel):
    header: VaultHeader
    secrets: Dict[str, str]
```

### EnvStore
Singleton for managing environment variables.

**TypeScript**
```typescript
class EnvStore {
  static async onStartup(envFile: string = '.env'): Promise<LoadResult>;
  static get(key: string, defaultValue?: string): string | undefined;
  static getOrThrow(key: string): string;
  static isInitialized(): boolean;
}
```

**Python**
```python
class EnvStore:
    @classmethod
    def on_startup(cls, env_file: str = ".env") -> LoadResult: ...
    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]: ...
    @classmethod
    def get_or_throw(cls, key: str) -> str: ...
    @classmethod
    def is_initialized(cls) -> bool: ...
```

## SDK
High-level operations for CLI, Agents, and Tools.

**TypeScript**
```typescript
const sdk = VaultFileSDK.create().withEnvPath('.env').build();
await sdk.loadConfig();
```

**Python**
```python
sdk = VaultFileSDK.create().with_env_path('.env').build()
sdk.load_config()
```

### SDK Operations
- `loadConfig()`: Loads configuration from default or configured path.
- `loadFromPath(path)`: Loads configuration from specific path.
- `validateFile(path)`: Validates integrity of a Vault File.
- `describeConfig()`: Returns metadata about loaded configuration.
- `getSecretSafe(key)`: Returns masked secret information.
- `diagnoseEnvStore()`: Checks initialization status.
