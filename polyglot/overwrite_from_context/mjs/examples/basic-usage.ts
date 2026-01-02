/**
 * Runtime Template Resolver - Basic Usage Examples
 *
 * This script demonstrates the core features of the runtime-template-resolver package:
 * - Template pattern resolution ({{variable.path}})
 * - Compute pattern resolution ({{fn:function_name}})
 * - Default value handling
 * - Scope enforcement (STARTUP vs REQUEST)
 * - Object resolution for nested configurations
 *
 * Run with: npx tsx examples/basic-usage.ts
 */

import { createRegistry, createResolver } from '../src/sdk.js';
import { ComputeScope } from '../src/options.js';

// =============================================================================
// Example 1: Basic Template Resolution
// =============================================================================
/**
 * Demonstrates basic template pattern resolution.
 *
 * Template patterns use the format {{path.to.value}} to extract values
 * from a context dictionary. Default values can be specified with | operator.
 */
async function example1_templateResolution(): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log('Example 1: Basic Template Resolution');
    console.log('='.repeat(60));

    // Create resolver
    const registry = createRegistry();
    const resolver = createResolver(registry);

    // Context data (simulating environment and config)
    const context = {
        env: {
            APP_NAME: 'MyApplication',
            DEBUG: 'true'
        },
        config: {
            database: {
                host: 'localhost',
                port: 5432
            }
        }
    };

    // Resolve template patterns
    const appName = await resolver.resolve('{{env.APP_NAME}}', context);
    const dbHost = await resolver.resolve('{{config.database.host}}', context);

    // Resolve with default values (for missing keys)
    const timeout = await resolver.resolve("{{config.timeout | '30'}}", context);
    const missing = await resolver.resolve("{{env.MISSING_VAR | 'default_value'}}", context);

    console.log(`App Name: ${appName}`);
    console.log(`DB Host: ${dbHost}`);
    console.log(`Timeout (default): ${timeout} (type: ${typeof timeout})`);
    console.log(`Missing var (default): ${missing}`);
}

// =============================================================================
// Example 2: Compute Function Resolution
// =============================================================================
/**
 * Demonstrates compute function registration and resolution.
 *
 * Compute patterns use the format {{fn:function_name}} to call registered
 * functions. Functions can access context and return computed values.
 */
async function example2_computeFunctions(): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log('Example 2: Compute Function Resolution');
    console.log('='.repeat(60));

    const registry = createRegistry();
    const resolver = createResolver(registry);

    // Register compute functions
    registry.register(
        'get_build_version',
        () => 'v2.1.0-build.1234',
        ComputeScope.STARTUP
    );

    registry.register(
        'get_connection_string',
        (ctx: any) => `postgresql://${ctx?.env?.DB_HOST || 'localhost'}:5432/app`,
        ComputeScope.STARTUP
    );

    // Simulate request-specific function
    let requestCounter = 0;

    registry.register(
        'get_request_id',
        () => {
            requestCounter++;
            return `req-${requestCounter.toString().padStart(5, '0')}`;
        },
        ComputeScope.REQUEST
    );

    // Context with environment
    const context = { env: { DB_HOST: 'db.example.com' } };

    // Resolve compute patterns
    const version = await resolver.resolve('{{fn:get_build_version}}', context);
    const connStr = await resolver.resolve('{{fn:get_connection_string}}', context);

    // REQUEST scope functions called multiple times get different results
    const reqId1 = await resolver.resolve('{{fn:get_request_id}}', context);
    const reqId2 = await resolver.resolve('{{fn:get_request_id}}', context);

    console.log(`Build Version: ${version}`);
    console.log(`Connection String: ${connStr}`);
    console.log(`Request ID (call 1): ${reqId1}`);
    console.log(`Request ID (call 2): ${reqId2}`);
}

// =============================================================================
// Example 3: Object Resolution
// =============================================================================
/**
 * Demonstrates resolving entire configuration objects.
 *
 * The resolveObject method recursively resolves all template and compute
 * patterns within nested dictionaries and lists.
 */
async function example3_objectResolution(): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log('Example 3: Object Resolution');
    console.log('='.repeat(60));

    const registry = createRegistry();
    const resolver = createResolver(registry);

    // Register a compute function
    registry.register(
        'get_timestamp',
        () => '2024-01-15T10:30:00Z',
        ComputeScope.STARTUP
    );

    // Configuration template with mixed patterns
    const configTemplate = {
        app: {
            name: "{{env.APP_NAME | 'DefaultApp'}}",
            version: "{{env.APP_VERSION | '1.0.0'}}",
            debug: "{{env.DEBUG | 'false'}}"
        },
        database: {
            host: "{{env.DB_HOST | 'localhost'}}",
            port: "{{env.DB_PORT | '5432'}}",
            pool_size: 10 // Non-template values are preserved
        },
        metadata: {
            build_time: '{{fn:get_timestamp}}',
            features: ['auth', 'logging', 'metrics'] // Lists preserved
        }
    };

    // Context
    const context = {
        env: {
            APP_NAME: 'ProductionApp',
            DB_HOST: 'db.prod.example.com'
        }
    };

    // Resolve entire object
    const resolvedConfig = await resolver.resolveObject(configTemplate, context);

    console.log('Resolved Configuration:');
    console.log(`  App Name: ${resolvedConfig.app.name}`);
    console.log(`  App Version: ${resolvedConfig.app.version}`);
    console.log(`  Debug: ${resolvedConfig.app.debug} (type: ${typeof resolvedConfig.app.debug})`);
    console.log(`  DB Host: ${resolvedConfig.database.host}`);
    console.log(`  DB Port: ${resolvedConfig.database.port} (type: ${typeof resolvedConfig.database.port})`);
    console.log(`  Pool Size: ${resolvedConfig.database.pool_size}`);
    console.log(`  Build Time: ${resolvedConfig.metadata.build_time}`);
    console.log(`  Features: ${JSON.stringify(resolvedConfig.metadata.features)}`);
}

// =============================================================================
// Example 4: Scope Enforcement
// =============================================================================
/**
 * Demonstrates STARTUP vs REQUEST scope enforcement.
 *
 * STARTUP scope functions:
 * - Run once at application startup
 * - Results are cached
 *
 * REQUEST scope functions:
 * - Run on each request
 * - Results are NOT cached
 */
async function example4_scopeEnforcement(): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log('Example 4: Scope Enforcement');
    console.log('='.repeat(60));

    const registry = createRegistry();
    const resolver = createResolver(registry);

    // Track calls to demonstrate caching
    let startupCalls = 0;
    let requestCalls = 0;

    registry.register(
        'startup_fn',
        () => {
            startupCalls++;
            return `startup-result-${startupCalls}`;
        },
        ComputeScope.STARTUP
    );

    registry.register(
        'request_fn',
        () => {
            requestCalls++;
            return `request-result-${requestCalls}`;
        },
        ComputeScope.REQUEST
    );

    const context = { env: {} };

    // STARTUP functions are cached
    console.log('STARTUP scope function (cached):');
    const result1 = await resolver.resolve('{{fn:startup_fn}}', context, ComputeScope.REQUEST);
    const result2 = await resolver.resolve('{{fn:startup_fn}}', context, ComputeScope.REQUEST);
    const result3 = await resolver.resolve('{{fn:startup_fn}}', context, ComputeScope.REQUEST);
    console.log(`  Call 1: ${result1}`);
    console.log(`  Call 2: ${result2}`);
    console.log(`  Call 3: ${result3}`);
    console.log(`  Total function executions: ${startupCalls}`);

    // REQUEST functions are called each time
    console.log('\nREQUEST scope function (not cached):');
    const rResult1 = await resolver.resolve('{{fn:request_fn}}', context, ComputeScope.REQUEST);
    const rResult2 = await resolver.resolve('{{fn:request_fn}}', context, ComputeScope.REQUEST);
    const rResult3 = await resolver.resolve('{{fn:request_fn}}', context, ComputeScope.REQUEST);
    console.log(`  Call 1: ${rResult1}`);
    console.log(`  Call 2: ${rResult2}`);
    console.log(`  Call 3: ${rResult3}`);
    console.log(`  Total function executions: ${requestCalls}`);
}

// =============================================================================
// Example 5: Default Value Type Inference
// =============================================================================
/**
 * Demonstrates automatic type inference for default values.
 *
 * Default values in patterns are automatically parsed:
 * - 'true'/'false' -> boolean
 * - Numeric strings -> number
 * - Other strings -> string
 */
async function example5_defaultTypeInference(): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log('Example 5: Default Value Type Inference');
    console.log('='.repeat(60));

    const registry = createRegistry();
    const resolver = createResolver(registry);

    const context = {}; // Empty context to trigger defaults

    // Different default value types
    const boolTrue = await resolver.resolve("{{missing | 'true'}}", context);
    const boolFalse = await resolver.resolve("{{missing | 'false'}}", context);
    const integer = await resolver.resolve("{{missing | '42'}}", context);
    const floatVal = await resolver.resolve("{{missing | '3.14'}}", context);
    const stringVal = await resolver.resolve("{{missing | 'hello'}}", context);

    console.log('Type inference for defaults:');
    console.log(`  'true' -> ${boolTrue} (type: ${typeof boolTrue})`);
    console.log(`  'false' -> ${boolFalse} (type: ${typeof boolFalse})`);
    console.log(`  '42' -> ${integer} (type: ${typeof integer})`);
    console.log(`  '3.14' -> ${floatVal} (type: ${typeof floatVal})`);
    console.log(`  'hello' -> ${stringVal} (type: ${typeof stringVal})`);
}

// =============================================================================
// Example 6: Realistic Configuration Scenario
// =============================================================================
/**
 * Demonstrates a realistic configuration resolution scenario.
 *
 * This example shows how the resolver would be used in a real application
 * to resolve configuration from environment variables and computed values.
 */
async function example6_realisticScenario(): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log('Example 6: Realistic Configuration Scenario');
    console.log('='.repeat(60));

    const registry = createRegistry();
    const resolver = createResolver(registry);

    // Register compute functions
    registry.register(
        'build_database_url',
        (ctx: any) => {
            const env = ctx?.env || {};
            const host = env.DB_HOST || 'localhost';
            const port = env.DB_PORT || '5432';
            const user = env.DB_USER || 'app';
            const password = env.DB_PASSWORD || 'secret';
            const name = env.DB_NAME || 'app_db';
            return `postgresql://${user}:${password}@${host}:${port}/${name}`;
        },
        ComputeScope.STARTUP
    );

    registry.register(
        'get_log_config',
        (ctx: any) => {
            const env = ctx?.env || {};
            const level = env.LOG_LEVEL || 'INFO';
            return { level, format: 'json', output: 'stdout' };
        },
        ComputeScope.STARTUP
    );

    // Simulated app.yaml configuration
    const appConfig = {
        server: {
            host: "{{env.HOST | '0.0.0.0'}}",
            port: "{{env.PORT | '8080'}}",
            workers: "{{env.WORKERS | '4'}}"
        },
        database: {
            url: '{{fn:build_database_url}}',
            pool_size: "{{env.DB_POOL_SIZE | '10'}}",
            timeout: "{{env.DB_TIMEOUT | '30'}}"
        },
        logging: '{{fn:get_log_config}}',
        features: {
            auth_enabled: "{{env.AUTH_ENABLED | 'true'}}",
            rate_limiting: "{{env.RATE_LIMIT | 'false'}}",
            metrics: "{{env.METRICS_ENABLED | 'true'}}"
        }
    };

    // Set up environment (simulating production)
    const originalEnv = { ...process.env };
    Object.assign(process.env, {
        DB_HOST: 'db.prod.example.com',
        DB_USER: 'app_user',
        DB_PASSWORD: 'super_secret',
        DB_NAME: 'production_db',
        LOG_LEVEL: 'WARNING',
        PORT: '3000',
        WORKERS: '8'
    });

    try {
        const context = { env: process.env };
        const resolved = await resolver.resolveObject(
            appConfig,
            context,
            ComputeScope.STARTUP
        );

        console.log('Resolved Production Configuration:');
        console.log('\nServer:');
        console.log(`  Host: ${resolved.server.host}`);
        console.log(`  Port: ${resolved.server.port} (type: ${typeof resolved.server.port})`);
        console.log(`  Workers: ${resolved.server.workers}`);

        console.log('\nDatabase:');
        console.log(`  URL: ${resolved.database.url}`);
        console.log(`  Pool Size: ${resolved.database.pool_size}`);
        console.log(`  Timeout: ${resolved.database.timeout}`);

        console.log('\nLogging:');
        console.log(`  Config: ${JSON.stringify(resolved.logging)}`);

        console.log('\nFeatures:');
        console.log(`  Auth Enabled: ${resolved.features.auth_enabled}`);
        console.log(`  Rate Limiting: ${resolved.features.rate_limiting}`);
        console.log(`  Metrics: ${resolved.features.metrics}`);
    } finally {
        // Restore original environment
        for (const key of Object.keys(process.env)) {
            if (!(key in originalEnv)) {
                delete process.env[key];
            }
        }
        Object.assign(process.env, originalEnv);
    }
}

// =============================================================================
// Main Runner
// =============================================================================
async function main(): Promise<void> {
    console.log('='.repeat(60));
    console.log('Runtime Template Resolver - Basic Usage Examples');
    console.log('='.repeat(60));

    await example1_templateResolution();
    await example2_computeFunctions();
    await example3_objectResolution();
    await example4_scopeEnforcement();
    await example5_defaultTypeInference();
    await example6_realisticScenario();

    console.log('\n' + '='.repeat(60));
    console.log('All examples completed successfully!');
    console.log('='.repeat(60));
}

main().catch(console.error);
