# Vault File Package

Polyglot configuration and secret management for Node.js and Python.

## Features
- **Unified Interface**: Consistent API across TS and Python.
- **Secure Handling**: Secret masking and safe retrieval.
- **SDK**: High-level tools for CLI and Agents.
- **Parity**: Identical serialization and behavior (mostly).

## Installation

### Node.js
```bash
pnpm add @internal/vault-file
```

### Python
```bash
poetry add vault-file
```

## Quick Start

### Node.js
```typescript
import { EnvStore } from '@internal/vault-file';

await EnvStore.onStartup();
const secret = EnvStore.getOrThrow('API_KEY');
```

### Python
```python
from vault_file import EnvStore

EnvStore.on_startup()
secret = EnvStore.get_or_throw('API_KEY')
```

## Documentation
- [API Reference](docs/API_REFERENCE.md)
- [Server Integration](docs/SERVER_INTEGRATION.md)
- [SDK Guide](docs/SDK_GUIDE.md)
- [Behavioral Differences](docs/BEHAVIORAL_DIFFERENCES.md)
