# Runtime Template Resolver - TypeScript/Node.js API Reference

Complete TypeScript API reference for the `runtime-template-resolver` package.

## Installation

```bash
npm install runtime-template-resolver
# or with yarn
yarn add runtime-template-resolver
```

## Module Exports

```typescript
import {
    // SDK Factory Functions
    createRegistry,
    createResolver,

    // Core Classes
    ComputeRegistry,
    ContextResolver,
    Security,

    // Configuration
    ComputeScope,
    MissingStrategy,
    ResolverOptions,

    // Logging
    Logger,
    LogLevel,

    // Errors
    ErrorCode,
    ResolveError,
    ComputeFunctionError,
    SecurityError,
    RecursionLimitError,
    ScopeViolationError,
    ValidationError
} from 'runtime-template-resolver';
```

## SDK Factory Functions

### createRegistry

```typescript
function createRegistry(logger?: Logger): ComputeRegistry;
```

Creates a new ComputeRegistry instance.

**Parameters:**
- `logger` (optional): Logger instance for debug output

**Returns:** New `ComputeRegistry` instance

### createResolver

```typescript
function createResolver(
    registry?: ComputeRegistry,
    options?: ResolverOptions,
    logger?: Logger
): ContextResolver;
```

Creates a new ContextResolver instance.

**Parameters:**
- `registry` (optional): Compute registry (created if not provided)
- `options` (optional): Resolver configuration
- `logger` (optional): Logger instance

**Returns:** New `ContextResolver` instance

## Core Classes

### ComputeRegistry

```typescript
class ComputeRegistry {
    constructor(logger?: Logger);

    /**
     * Register a compute function.
     * @param name - Function name (must match ^[a-zA-Z_][a-zA-Z0-9_]*$)
     * @param fn - Callable that optionally accepts context
     * @param scope - ComputeScope.STARTUP or ComputeScope.REQUEST
     * @throws Error if name is empty or invalid
     */
    register(name: string, fn: ComputeFunction, scope: ComputeScope): void;

    /** Remove a registered function */
    unregister(name: string): void;

    /** Check if function is registered */
    has(name: string): boolean;

    /** Get list of registered function names */
    list(): string[];

    /** Get scope of registered function */
    getScope(name: string): ComputeScope | undefined;

    /** Clear all registered functions and cache */
    clear(): void;

    /** Clear cached STARTUP results only */
    clearCache(): void;

    /**
     * Execute a registered function.
     * @param name - Function name
     * @param context - Optional context passed to function
     * @returns Function result (cached for STARTUP scope)
     * @throws ComputeFunctionError if function not found or execution fails
     */
    resolve(name: string, context?: any): Promise<any>;
}

type ComputeFunction = (context?: any) => any | Promise<any>;
```

### ContextResolver

```typescript
class ContextResolver {
    constructor(registry: ComputeRegistry, options?: ResolverOptions);

    /** Check if expression is a compute pattern ({{fn:...}}) */
    isComputePattern(expression: string): boolean;

    /**
     * Resolve a single expression.
     * @param expression - Pattern string or pass-through value
     * @param context - Context object for variable lookup
     * @param scope - Resolution scope (STARTUP or REQUEST)
     * @param depth - Current recursion depth (internal)
     * @returns Resolved value with type inference
     * @throws RecursionLimitError if maxDepth exceeded
     * @throws ScopeViolationError if REQUEST function called in STARTUP
     * @throws ComputeFunctionError if compute function fails
     * @throws SecurityError if path validation fails
     */
    resolve(
        expression: any,
        context: Record<string, any>,
        scope?: ComputeScope,
        depth?: number
    ): Promise<any>;

    /**
     * Recursively resolve all patterns in nested object.
     * @param obj - Object, array, or scalar value
     * @param context - Context object for variable lookup
     * @param scope - Resolution scope
     * @param depth - Current recursion depth
     * @returns Deep copy with all patterns resolved
     */
    resolveObject(
        obj: any,
        context: Record<string, any>,
        scope?: ComputeScope,
        depth?: number
    ): Promise<any>;

    /** Resolve multiple expressions in parallel */
    resolveMany(
        expressions: any[],
        context: Record<string, any>,
        scope?: ComputeScope
    ): Promise<any[]>;
}
```

### Security

```typescript
class Security {
    private static PATH_PATTERN: RegExp;  // /^[a-zA-Z][a-zA-Z0-9_.]*$/

    private static BLOCKED_PATTERNS: Set<string>;
    // "__proto__", "__class__", "__dict__", "constructor", "prototype"

    /**
     * Validate context path for security.
     * @param path - Dot-notation path string
     * @throws SecurityError if path is blocked or invalid
     */
    static validatePath(path: string): void;
}
```

## Configuration

### ComputeScope

```typescript
enum ComputeScope {
    STARTUP = 'STARTUP',   // Cached at startup
    REQUEST = 'REQUEST'    // Executed per-request
}
```

### MissingStrategy

```typescript
enum MissingStrategy {
    ERROR = 'ERROR',       // Throw error on missing
    DEFAULT = 'DEFAULT',   // Return undefined
    IGNORE = 'IGNORE'      // Return original pattern
}
```

### ResolverOptions

```typescript
interface ResolverOptions {
    logger?: Logger;
    maxDepth?: number;              // Default: 10
    missingStrategy?: MissingStrategy;  // Default: ERROR
}
```

## Errors

### Error Hierarchy

```typescript
class ResolveError extends Error {
    code: string;
    context: Record<string, any>;

    constructor(message: string, code: string, context?: Record<string, any>);
}

class ComputeFunctionError extends ResolveError {}
class SecurityError extends ResolveError {}
class RecursionLimitError extends ResolveError {}
class ScopeViolationError extends ResolveError {}
class ValidationError extends ResolveError {}
```

### ErrorCode

```typescript
enum ErrorCode {
    COMPUTE_FUNCTION_NOT_FOUND = 'ERR_COMPUTE_NOT_FOUND',
    COMPUTE_FUNCTION_FAILED = 'ERR_COMPUTE_FAILED',
    SECURITY_BLOCKED_PATH = 'ERR_SECURITY_PATH',
    RECURSION_LIMIT = 'ERR_RECURSION_LIMIT',
    SCOPE_VIOLATION = 'ERR_SCOPE_VIOLATION',
    VALIDATION_ERROR = 'ERR_VALIDATION_ERROR'
}
```

## Fastify Integration

```typescript
import { contextResolverPlugin } from 'runtime-template-resolver/integrations/fastify';
```

### ContextResolverPluginOptions

```typescript
interface ContextResolverPluginOptions {
    config: Record<string, any>;      // Raw configuration template
    registry?: ComputeRegistry;       // Compute registry (created if not provided)
    instanceProperty?: string;        // Property name on fastify (default: 'config')
    requestProperty?: string;         // Property name on request (default: 'config')
    logger?: Logger;                  // Custom logger
}
```

### contextResolverPlugin

Fastify plugin wrapped with `fastify-plugin` for proper encapsulation.

**Side Effects:**
- Decorates `fastify[instanceProperty]` with STARTUP-resolved config
- Adds `onRequest` hook to resolve REQUEST-scope config
- Decorates `request.resolveContext(pattern)` helper method

## Usage Examples

### Basic Resolution

```typescript
import { createRegistry, createResolver, ComputeScope } from 'runtime-template-resolver';

const registry = createRegistry();
const resolver = createResolver(registry);

// Register functions
registry.register('getVersion', () => '1.0.0', ComputeScope.STARTUP);

// Resolve patterns
const context = { env: process.env };

const name = await resolver.resolve('{{env.APP_NAME}}', context);
const version = await resolver.resolve('{{fn:getVersion}}', context);
const missing = await resolver.resolve("{{env.MISSING | 'default'}}", context);

console.log(`Name: ${name}, Version: ${version}, Missing: ${missing}`);
```

### Object Resolution

```typescript
const config = {
    app: {
        name: "{{env.APP_NAME | 'MyApp'}}",
        version: '{{fn:getVersion}}',
        debug: "{{env.DEBUG | 'false'}}"
    },
    database: {
        host: "{{env.DB_HOST | 'localhost'}}",
        port: "{{env.DB_PORT | '5432'}}"
    }
};

const resolved = await resolver.resolveObject(config, context, ComputeScope.STARTUP);
// resolved.app.name -> 'MyApp' (string)
// resolved.app.debug -> false (boolean)
// resolved.database.port -> 5432 (number)
```

### Fastify Integration

```typescript
import Fastify from 'fastify';
import { createRegistry, ComputeScope } from 'runtime-template-resolver';
import { contextResolverPlugin } from 'runtime-template-resolver/integrations/fastify';

const registry = createRegistry();
registry.register('getVersion', () => '1.0.0', ComputeScope.STARTUP);

const config = {
    app: { name: "{{env.APP_NAME | 'MyApp'}}", version: '{{fn:getVersion}}' }
};

const app = Fastify();

await app.register(contextResolverPlugin, {
    config,
    registry,
    instanceProperty: 'config',
    requestProperty: 'config'
});

app.get('/health', async (request, reply) => {
    return {
        status: 'healthy',
        app: app.config.app.name,
        version: app.config.app.version
    };
});

app.get('/resolve', async (request, reply) => {
    const value = await request.resolveContext('{{fn:getRequestId}}');
    return { value };
});

await app.listen({ port: 3000 });
```

## Type Augmentation

For TypeScript users, augment Fastify types:

```typescript
declare module 'fastify' {
    interface FastifyInstance {
        config: Record<string, any>;
    }
    interface FastifyRequest {
        config: Record<string, any>;
        resolveContext: (pattern: string) => Promise<any>;
    }
}
```
