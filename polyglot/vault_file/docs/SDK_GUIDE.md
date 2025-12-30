# Vault File SDK Guide

The Vault File SDK provides a high-level API for CLI tools, LLM Agents, and Developer Tools to interact with the Vault File system.

## Usage

### Node.js

```typescript
import { VaultFileSDK } from '@internal/vault-file';

// Initialize SDK
const sdk = VaultFileSDK.create()
  .withEnvPath('./.env')
  .build();

// Load Configuration
const result = await sdk.loadConfig();
if (result.success) {
  console.log('Loaded:', result.data.totalVarsLoaded);
}

// Check for missing keys
const missing = await sdk.findMissingRequired(['API_KEY', 'DB_URL']);
```

### Python

```python
from vault_file import VaultFileSDK

# Initialize SDK
sdk = (VaultFileSDK.create()
  .with_env_path('./.env')
  .build())

# Load Configuration
result = sdk.load_config()
if result.success:
    print(f"Loaded: {result.data.total_vars_loaded}")

# Check for missing keys
missing = sdk.find_missing_required(['API_KEY', 'DB_URL'])
```

## Features

- **CLI Operations**: `loadFromPath`, `validateFile`
- **Agent Operations**: `describeConfig`, `getSecretSafe` (masked)
- **Dev Tools**: `diagnoseEnvStore`, `findMissingRequired`
