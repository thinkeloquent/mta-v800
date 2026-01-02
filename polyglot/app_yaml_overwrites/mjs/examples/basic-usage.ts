#!/usr/bin/env npx tsx
/**
 * app_yaml_overwrites - Basic Usage Examples
 * ==========================================
 *
 * This script demonstrates core features of the app_yaml_overwrites package:
 * - Logger: Standardized JSON logging with LOG_LEVEL control
 * - ContextBuilder: Building resolution context with extenders
 * - OverwriteMerger: Deep merging configuration overwrites
 *
 * Run with: npx tsx basic-usage.ts
 */

import { Logger } from '../src/logger.js';
import { ContextBuilder, ContextExtender } from '../src/context-builder.js';
import { applyOverwrites } from '../src/overwrite-merger.js';

// =============================================================================
// Example 1: Logger Factory Pattern
// =============================================================================
/**
 * Demonstrates the Logger.create() factory pattern for standardized logging.
 *
 * The logger outputs JSON-formatted logs with:
 * - timestamp
 * - level (DEBUG, INFO, WARN, ERROR)
 * - context (package:filename)
 * - message
 * - data (optional object)
 */
function example1_loggerFactory(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 1: Logger Factory Pattern');
    console.log('='.repeat(60));

    // Create logger using factory pattern
    const logger = Logger.create('my-service', 'basic-usage.ts');

    // Log at different levels
    logger.debug('This is a debug message');
    logger.info('Application started', { version: '1.0.0', env: 'development' });
    logger.warn('Configuration missing, using defaults');
    logger.error('Failed to connect', { host: 'localhost', port: 5432 });

    console.log('\nLogger created with context: my-service:basic-usage.ts');
}

// =============================================================================
// Example 2: Log Level Control
// =============================================================================
/**
 * Demonstrates LOG_LEVEL environment variable control.
 *
 * Levels (in order): trace, debug, info, warn, error
 * Setting LOG_LEVEL=info will suppress debug and trace messages.
 */
function example2_logLevelControl(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 2: Log Level Control');
    console.log('='.repeat(60));

    // Store original level
    const originalLevel = process.env.LOG_LEVEL;

    // Set to INFO level - should suppress DEBUG
    process.env.LOG_LEVEL = 'info';
    const logger = Logger.create('log-demo', 'basic-usage.ts');

    console.log('\nWith LOG_LEVEL=info:');
    logger.debug('This DEBUG message should be suppressed');
    logger.info('This INFO message should appear');

    // Set to ERROR level - should only show errors
    process.env.LOG_LEVEL = 'error';
    const logger2 = Logger.create('log-demo-2', 'basic-usage.ts');

    console.log('\nWith LOG_LEVEL=error:');
    logger2.info('This INFO message should be suppressed');
    logger2.error('This ERROR message should appear');

    // Restore original level
    if (originalLevel !== undefined) {
        process.env.LOG_LEVEL = originalLevel;
    } else {
        delete process.env.LOG_LEVEL;
    }
}

// =============================================================================
// Example 3: Context Builder - Basic Usage
// =============================================================================
/**
 * Demonstrates building a resolution context with ContextBuilder.
 *
 * The context contains:
 * - env: Environment variables (defaults to process.env)
 * - config: Raw configuration object
 * - app: Application metadata
 * - state: Runtime state
 * - request: HTTP request object (optional)
 */
async function example3_contextBuilderBasic(): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log('Example 3: Context Builder - Basic Usage');
    console.log('='.repeat(60));

    // Build context with basic options
    const context = await ContextBuilder.build({
        config: {
            app: { name: 'MyApp', version: '1.0.0' },
            database: { host: 'localhost', port: 5432 }
        },
        app: { name: 'MyApp', version: '1.0.0' },
        state: { requestCount: 42 }
    });

    console.log(`\nContext keys: ${Object.keys(context).join(', ')}`);
    console.log(`App name: ${context.app.name}`);
    console.log(`State: ${JSON.stringify(context.state)}`);
    console.log(`Has env: ${'env' in context}`);
}

// =============================================================================
// Example 4: Context Builder - With Extenders
// =============================================================================
/**
 * Demonstrates context extenders for adding custom context.
 *
 * Extenders are async functions that receive the current context
 * and optionally the request, returning additional context keys.
 * They run sequentially and can see results from previous extenders.
 */
async function example4_contextBuilderExtenders(): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log('Example 4: Context Builder - With Extenders');
    console.log('='.repeat(60));

    // Define auth extender - adds authentication context
    const authExtender: ContextExtender = async (ctx, request) => {
        // Simulate fetching auth from request headers or session
        return {
            auth: {
                userId: 'user-123',
                roles: ['admin', 'user'],
                token: 'bearer-xxx'
            }
        };
    };

    // Define tenant extender - adds multi-tenancy context
    const tenantExtender: ContextExtender = async (ctx, request) => {
        // Can access auth from previous extender
        const userId = ctx.auth?.userId || 'anonymous';
        return {
            tenant: {
                id: 'tenant-456',
                name: 'Acme Corp',
                owner: userId
            }
        };
    };

    // Build context with extenders
    const context = await ContextBuilder.build(
        { config: { app: { name: 'MultiTenantApp' } } },
        [authExtender, tenantExtender]
    );

    console.log(`\nContext keys: ${Object.keys(context).join(', ')}`);
    console.log(`Auth user: ${context.auth.userId}`);
    console.log(`Tenant: ${context.tenant.name}`);
    console.log(`Tenant owner: ${context.tenant.owner}`);
}

// =============================================================================
// Example 5: Overwrite Merger - Basic Merge
// =============================================================================
/**
 * Demonstrates basic configuration merging with applyOverwrites.
 *
 * The merge is deep - nested objects are merged recursively,
 * with overwrites taking precedence.
 */
function example5_overwriteMergerBasic(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 5: Overwrite Merger - Basic Merge');
    console.log('='.repeat(60));

    // Original configuration with some null placeholders
    const original = {
        database: {
            host: 'localhost',
            port: 5432,
            password: null  // Placeholder for runtime value
        },
        cache: {
            enabled: true,
            ttl: 3600
        }
    };

    // Overwrites to apply (e.g., from resolved templates)
    const overwrites = {
        database: {
            password: 'secret-from-vault'  // Fill in the placeholder
        },
        cache: {
            ttl: 7200  // Override default TTL
        }
    };

    const result = applyOverwrites(original, overwrites);

    console.log(`\nOriginal password: ${original.database.password}`);
    console.log(`Merged password: ${result.database.password}`);
    console.log(`Original TTL: ${original.cache.ttl}`);
    console.log(`Merged TTL: ${result.cache.ttl}`);
    console.log(`Host preserved: ${result.database.host}`);
}

// =============================================================================
// Example 6: Overwrite Merger - overwrite_from_context Pattern
// =============================================================================
/**
 * Demonstrates the overwrite_from_context pattern used in app.yaml.
 *
 * This pattern allows configurations to define which values should
 * be resolved at runtime and merged back into the parent config.
 */
function example6_overwriteFromContext(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 6: overwrite_from_context Pattern');
    console.log('='.repeat(60));

    // Provider configuration with overwrite_from_context section
    const providerConfig = {
        baseUrl: 'https://api.example.com',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': null,  // Will be filled from context
            'X-App-Name': null      // Will be filled from context
        },
        timeout: 30,
        overwrite_from_context: {
            headers: {
                'Authorization': 'Bearer resolved-jwt-token',
                'X-App-Name': 'MyApp'
            }
        }
    };

    // Apply the overwrites (simulating what the resolver does)
    const resolved = applyOverwrites(
        providerConfig,
        providerConfig.overwrite_from_context
    );

    console.log('\nBefore merge:');
    console.log(`  Authorization: ${providerConfig.headers.Authorization}`);
    console.log(`  X-App-Name: ${providerConfig.headers['X-App-Name']}`);

    console.log('\nAfter merge:');
    console.log(`  Authorization: ${resolved.headers.Authorization}`);
    console.log(`  X-App-Name: ${resolved.headers['X-App-Name']}`);
    console.log(`  Content-Type (preserved): ${resolved.headers['Content-Type']}`);
}

// =============================================================================
// Example 7: Full Integration Pattern
// =============================================================================
/**
 * Demonstrates combining all components in a realistic scenario.
 *
 * This shows how the pieces work together:
 * 1. Logger for observability
 * 2. ContextBuilder for preparing resolution context
 * 3. OverwriteMerger for applying resolved values
 */
async function example7_fullIntegration(): Promise<void> {
    console.log('\n' + '='.repeat(60));
    console.log('Example 7: Full Integration Pattern');
    console.log('='.repeat(60));

    // Setup logger
    const logger = Logger.create('integration-demo', 'basic-usage.ts');
    logger.info('Starting configuration resolution');

    // Simulate raw configuration (would come from AppYamlConfig)
    const rawConfig = {
        app: { name: 'IntegrationDemo', version: '2.0.0' },
        providers: {
            paymentApi: {
                baseUrl: 'https://pay.example.com',
                headers: {
                    'X-Api-Key': null,
                    'X-Tenant-Id': null
                },
                overwrite_from_context: {
                    headers: {
                        'X-Api-Key': '{{env.PAYMENT_API_KEY}}',
                        'X-Tenant-Id': '{{tenant.id}}'
                    }
                }
            }
        }
    };

    // Define context extenders
    const apiKeyExtender: ContextExtender = async (ctx, req) => {
        // Simulate resolving API key from secrets
        return { secrets: { paymentApiKey: 'sk_live_xxx' } };
    };

    const tenantExtender: ContextExtender = async (ctx, req) => {
        return { tenant: { id: 'tenant-789' } };
    };

    // Build context
    const context = await ContextBuilder.build(
        {
            config: rawConfig,
            app: rawConfig.app,
            env: { PAYMENT_API_KEY: 'sk_live_xxx' } as any
        },
        [apiKeyExtender, tenantExtender]
    );

    logger.debug('Context built', { keys: Object.keys(context) });

    // Simulate resolved overwrites (in real use, RuntimeTemplateResolver does this)
    const resolvedOverwrites = {
        headers: {
            'X-Api-Key': context.env.PAYMENT_API_KEY,
            'X-Tenant-Id': context.tenant.id
        }
    };

    // Apply overwrites
    const provider = rawConfig.providers.paymentApi;
    const resolvedProvider = applyOverwrites(provider, resolvedOverwrites);

    logger.info('Configuration resolved', { provider: 'paymentApi' });

    console.log('\nResolved paymentApi provider:');
    console.log(`  Base URL: ${resolvedProvider.baseUrl}`);
    console.log(`  X-Api-Key: ${resolvedProvider.headers['X-Api-Key']}`);
    console.log(`  X-Tenant-Id: ${resolvedProvider.headers['X-Tenant-Id']}`);
}

// =============================================================================
// Main Runner
// =============================================================================
async function main(): Promise<void> {
    console.log('='.repeat(60));
    console.log('app_yaml_overwrites - Basic Usage Examples');
    console.log('='.repeat(60));

    // Synchronous examples
    example1_loggerFactory();
    example2_logLevelControl();

    // Async examples
    await example3_contextBuilderBasic();
    await example4_contextBuilderExtenders();

    // Synchronous examples
    example5_overwriteMergerBasic();
    example6_overwriteFromContext();

    // Full integration
    await example7_fullIntegration();

    console.log('\n' + '='.repeat(60));
    console.log('All examples completed!');
    console.log('='.repeat(60));
}

main().catch(console.error);
