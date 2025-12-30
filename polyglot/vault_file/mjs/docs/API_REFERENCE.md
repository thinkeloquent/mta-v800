# Node.js API Reference

## Core Components

### EnvStore
Singleton for managing environment variables.

```typescript
class EnvStore {
  /**
   * Async startup hook to load environment variables.
   * Priority: process.env > Internal Store
   * 
   * @param envFile - Path to .env file (default: '.env')
   * @param logger - Optional custom logger instance
   */
  static async onStartup(envFile?: string, logger?: IVaultFileLogger): Promise<LoadResult>;

  /**
   * Get value from store.
   * 
   * @param key - Environment variable key
   * @param defaultValue - Value to return if key not found
   */
  static get(key: string, defaultValue?: string): string | undefined;

  /**
   * Get value or throw if missing.
   * 
   * @param key - Environment variable key
   * @throws EnvKeyNotFoundError
   */
  static getOrThrow(key: string): string;

  /**
   * Check if onStartup has been called.
   */
  static isInitialized(): boolean;
}
```

## SDK

### VaultFileSDK
High-level SDK for interacting with Vault File.

```typescript
const sdk = VaultFileSDK.create()
  .withEnvPath('.env')
  .build();
```

#### Builder Methods
*   `withEnvPath(path: string): VaultFileSDKBuilder` - Set path to .env file
*   `withBase64Parsers(parsers: Record<string, (val: string) => any>): VaultFileSDKBuilder` - Set custom parsers

#### Operations
*   `loadConfig(): Promise<SDKResult<LoadResult>>` - Load configuration
*   `loadFromPath(filePath: string): Promise<SDKResult<LoadResult>>` - Load from specific path
*   `validateFile(filePath: string): Promise<SDKResult<ValidationResult>>` - Validate file integrity
*   `describeConfig(): SDKResult<ConfigDescription>` - Get config metadata
*   `getSecretSafe(key: string): SDKResult<SecretInfo>` - Get masked secret
