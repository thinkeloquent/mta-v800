/**
 * Runtime Template Resolver - Fastify Integration Example
 *
 * This example demonstrates how to integrate the runtime-template-resolver
 * package with a Fastify application, including:
 * - Configuration resolution at startup
 * - Request-scoped resolution
 * - Plugin patterns
 * - Health check and demo routes
 *
 * Run with: npx tsx watch examples/fastify-app/server.ts
 */

import Fastify, { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { createRegistry } from '../../src/sdk.js';
import { ComputeScope } from '../../src/options.js';
import { contextResolverPlugin } from '../../src/integrations/fastify.js';

// =============================================================================
// Type Augmentation
// =============================================================================
declare module 'fastify' {
    interface FastifyInstance {
        config: Record<string, any>;
    }
    interface FastifyRequest {
        config: Record<string, any>;
        resolveContext: (pattern: string) => Promise<any>;
    }
}

// =============================================================================
// Mock Configuration (simulating app.yaml)
// =============================================================================
const MOCK_APP_CONFIG = {
    app: {
        name: "{{env.APP_NAME | 'Fastify Demo'}}",
        version: '{{fn:get_app_version}}',
        environment: "{{env.ENVIRONMENT | 'development'}}",
        debug: "{{env.DEBUG | 'true'}}"
    },
    server: {
        host: "{{env.HOST | '0.0.0.0'}}",
        port: "{{env.PORT | '3000'}}"
    },
    database: {
        connection: '{{fn:build_connection_string}}',
        pool_size: "{{env.DB_POOL_SIZE | '5'}}",
        timeout: "{{env.DB_TIMEOUT | '30'}}"
    },
    features: {
        auth_enabled: "{{env.AUTH_ENABLED | 'false'}}",
        metrics_enabled: "{{env.METRICS_ENABLED | 'true'}}",
        rate_limit: "{{env.RATE_LIMIT | '100'}}"
    },
    metadata: {
        started_at: '{{fn:get_startup_time}}'
    }
};

// =============================================================================
// Compute Registry Setup
// =============================================================================
const registry = createRegistry();

// STARTUP scope functions (cached, run once)
registry.register(
    'get_app_version',
    () => '1.2.3-demo',
    ComputeScope.STARTUP
);

registry.register(
    'get_startup_time',
    () => new Date().toISOString(),
    ComputeScope.STARTUP
);

registry.register(
    'build_connection_string',
    (ctx: any) => {
        const env = ctx?.env || process.env;
        const user = env.DB_USER || 'app';
        const password = env.DB_PASSWORD || 'secret';
        const host = env.DB_HOST || 'localhost';
        const port = env.DB_PORT || '5432';
        const name = env.DB_NAME || 'demo_db';
        return `postgresql://${user}:${password}@${host}:${port}/${name}`;
    },
    ComputeScope.STARTUP
);

// REQUEST scope functions (run per-request)
let requestCounter = 0;

registry.register(
    'get_request_id',
    () => {
        requestCounter++;
        return `req-${requestCounter.toString().padStart(8, '0')}`;
    },
    ComputeScope.REQUEST
);

// =============================================================================
// Fastify Application
// =============================================================================
const app: FastifyInstance = Fastify({
    logger: {
        level: 'info',
        transport: {
            target: 'pino-pretty',
            options: {
                translateTime: 'HH:MM:ss Z',
                ignore: 'pid,hostname'
            }
        }
    }
});

// =============================================================================
// Register Context Resolver Plugin
// =============================================================================
app.register(contextResolverPlugin, {
    config: MOCK_APP_CONFIG,
    registry: registry,
    instanceProperty: 'config',
    requestProperty: 'config'
});

// =============================================================================
// Routes
// =============================================================================

// Health check
app.get('/health', async (request: FastifyRequest, reply: FastifyReply) => {
    return {
        status: 'healthy',
        app: app.config.app.name,
        version: app.config.app.version,
        environment: app.config.app.environment,
        uptime: process.uptime()
    };
});

// Get startup-resolved configuration
app.get('/config/startup', async (request: FastifyRequest, reply: FastifyReply) => {
    return {
        resolved_at: 'startup',
        config: app.config
    };
});

// Get request-resolved configuration
app.get('/config', async (request: FastifyRequest, reply: FastifyReply) => {
    return {
        resolved_at: 'request',
        config: request.config
    };
});

// Get unique request ID using resolver
app.get('/request-id', async (request: FastifyRequest, reply: FastifyReply) => {
    const requestId = await request.resolveContext('{{fn:get_request_id}}');
    return {
        request_id: requestId,
        method: request.method,
        path: request.url
    };
});

// Get feature flags
app.get('/demo/features', async (request: FastifyRequest, reply: FastifyReply) => {
    return {
        features: request.config.features,
        note: 'Feature flags are resolved from environment variables with defaults'
    };
});

// Get database configuration (sanitized)
app.get('/demo/database', async (request: FastifyRequest, reply: FastifyReply) => {
    const dbConfig = request.config.database;

    // Sanitize connection string (redact password)
    let connStr = dbConfig.connection;
    if (connStr.includes('@')) {
        const parts = connStr.split('://');
        if (parts.length === 2) {
            const authAndRest = parts[1].split('@');
            if (authAndRest.length === 2 && authAndRest[0].includes(':')) {
                const user = authAndRest[0].split(':')[0];
                connStr = `${parts[0]}://${user}:****@${authAndRest[1]}`;
            }
        }
    }

    return {
        connection: connStr,
        pool_size: dbConfig.pool_size,
        timeout: dbConfig.timeout
    };
});

// Demo endpoint to resolve arbitrary patterns
interface ResolveQuery {
    pattern?: string;
}

app.get<{ Querystring: ResolveQuery }>('/demo/resolve', async (request, reply) => {
    const pattern = request.query.pattern || "{{env.HOME | '/home/user'}}";

    try {
        const result = await request.resolveContext(pattern);
        return {
            pattern,
            resolved: result,
            type: typeof result
        };
    } catch (error: any) {
        reply.status(400);
        return {
            pattern,
            error: error.message,
            error_type: error.constructor.name
        };
    }
});

// Demo: Multiple requests showing REQUEST scope behavior
app.get('/demo/counter', async (request: FastifyRequest, reply: FastifyReply) => {
    // Call the REQUEST scope function multiple times
    const id1 = await request.resolveContext('{{fn:get_request_id}}');
    const id2 = await request.resolveContext('{{fn:get_request_id}}');
    const id3 = await request.resolveContext('{{fn:get_request_id}}');

    return {
        message: 'REQUEST scope functions are called each time',
        request_ids: [id1, id2, id3],
        note: 'Each call to get_request_id returns a new unique ID'
    };
});

// Demo: Show difference between STARTUP and REQUEST resolution
app.get('/demo/scopes', async (request: FastifyRequest, reply: FastifyReply) => {
    return {
        startup_config: {
            description: 'Resolved once at application start, cached',
            app_version: app.config.app.version,
            started_at: app.config.metadata.started_at,
            database_connection: app.config.database.connection
        },
        request_config: {
            description: 'Resolved on each request',
            app_version: request.config.app.version,
            note: 'STARTUP functions return cached values even during REQUEST resolution'
        }
    };
});

// =============================================================================
// Error Handler
// =============================================================================
app.setErrorHandler((error, request, reply) => {
    app.log.error(error);
    reply.status(500).send({
        error: error.message,
        type: error.constructor.name,
        path: request.url
    });
});

// =============================================================================
// Start Server
// =============================================================================
const start = async () => {
    try {
        const port = parseInt(process.env.PORT || '3000', 10);
        const host = process.env.HOST || '0.0.0.0';

        await app.listen({ port, host });

        console.log('\n' + '='.repeat(60));
        console.log('Runtime Template Resolver - Fastify Demo Server');
        console.log('='.repeat(60));
        console.log(`\nServer running at http://${host}:${port}`);
        console.log('\nAvailable routes:');
        console.log('  GET /health           - Health check');
        console.log('  GET /config           - Request-resolved configuration');
        console.log('  GET /config/startup   - Startup-resolved configuration');
        console.log('  GET /request-id       - Generate unique request ID');
        console.log('  GET /demo/features    - Feature flags');
        console.log('  GET /demo/database    - Database config (sanitized)');
        console.log('  GET /demo/resolve     - Resolve arbitrary patterns');
        console.log('  GET /demo/counter     - REQUEST scope demo');
        console.log('  GET /demo/scopes      - STARTUP vs REQUEST comparison');
        console.log('\n' + '='.repeat(60));
    } catch (err) {
        app.log.error(err);
        process.exit(1);
    }
};

start();
