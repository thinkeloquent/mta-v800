/**
 * Fastify Integration Example for app_yaml_overwrites
 * ====================================================
 *
 * This example demonstrates how to integrate app_yaml_overwrites with Fastify:
 * - Server decoration for configuration access
 * - Context building with request-scoped data
 * - Health check endpoints
 * - Provider configuration endpoints
 *
 * Run with: npx tsx watch fastify-app/server.ts
 */

import Fastify, { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { Logger } from '../../src/logger.js';
import { ContextBuilder, ContextExtender } from '../../src/context-builder.js';
import { applyOverwrites } from '../../src/overwrite-merger.js';

// =============================================================================
// Type Augmentation
// =============================================================================

declare module 'fastify' {
    interface FastifyInstance {
        config: AppConfig;
        logger: Logger;
    }
}

// =============================================================================
// Types
// =============================================================================

interface AppConfig {
    app: {
        name: string;
        version: string;
        environment: string;
    };
    providers: Record<string, ProviderConfig>;
    features: {
        enableCaching: boolean;
        cacheTtl: number;
    };
}

interface ProviderConfig {
    baseUrl: string;
    timeout: number;
    headers: Record<string, string | null>;
    overwrite_from_context?: Record<string, any>;
}

interface ResolvedContext {
    env: Record<string, string>;
    config: AppConfig;
    app: AppConfig['app'];
    auth: { token: string | null; authenticated: boolean };
    tenant: { id: string; name: string };
    request: { headers: Record<string, string> };
}

// =============================================================================
// Mock Configuration (would use AppYamlConfig in production)
// =============================================================================

const MOCK_CONFIG: AppConfig = {
    app: {
        name: 'Fastify Example',
        version: '1.0.0',
        environment: 'development'
    },
    providers: {
        userApi: {
            baseUrl: 'https://users.example.com',
            timeout: 30,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': null,
                'X-Request-Id': null
            },
            overwrite_from_context: {
                headers: {
                    'Authorization': 'Bearer {{auth.token}}',
                    'X-Request-Id': '{{request.headers.x-request-id}}'
                }
            }
        },
        paymentApi: {
            baseUrl: 'https://payments.example.com',
            timeout: 60,
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
    },
    features: {
        enableCaching: true,
        cacheTtl: 3600
    }
};

// =============================================================================
// Context Extenders
// =============================================================================

const authExtender: ContextExtender = async (ctx, request) => {
    const authHeader = request?.headers?.['authorization'] as string | undefined;
    return {
        auth: {
            token: authHeader?.replace('Bearer ', '') || null,
            authenticated: !!authHeader
        }
    };
};

const tenantExtender: ContextExtender = async (ctx, request) => {
    const tenantId = (request?.headers?.['x-tenant-id'] as string) || 'default';
    return {
        tenant: {
            id: tenantId,
            name: `Tenant ${tenantId}`
        }
    };
};

// =============================================================================
// Helper Functions
// =============================================================================

function resolveTemplates(obj: any, context: ResolvedContext): any {
    if (typeof obj === 'string') {
        if (obj.startsWith('{{') && obj.endsWith('}}')) {
            const path = obj.slice(2, -2).trim();
            return getNestedValue(context, path);
        }
        return obj;
    } else if (Array.isArray(obj)) {
        return obj.map(item => resolveTemplates(item, context));
    } else if (obj && typeof obj === 'object') {
        return Object.fromEntries(
            Object.entries(obj).map(([k, v]) => [k, resolveTemplates(v, context)])
        );
    }
    return obj;
}

function getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((acc, key) => acc?.[key], obj);
}

async function buildContext(request: FastifyRequest, config: AppConfig): Promise<ResolvedContext> {
    const context = await ContextBuilder.build(
        {
            config,
            app: config.app,
            env: process.env as Record<string, string>,
            request
        },
        [authExtender, tenantExtender]
    );

    // Add request headers to context
    context.request = {
        headers: Object.fromEntries(
            Object.entries(request.headers).map(([k, v]) => [k, String(v)])
        )
    };

    return context as ResolvedContext;
}

// =============================================================================
// Server Setup
// =============================================================================

async function buildServer(): Promise<FastifyInstance> {
    const server = Fastify({
        logger: false // We use our own logger
    });

    const logger = Logger.create('fastify-example', 'server.ts');

    // Decorate server with config and logger
    server.decorate('config', MOCK_CONFIG);
    server.decorate('logger', logger);

    // Request counter
    let requestCount = 0;

    // =============================================================================
    // Health Routes
    // =============================================================================

    server.get('/health', async (request, reply) => {
        requestCount++;
        return {
            status: 'healthy',
            appName: server.config.app.name,
            version: server.config.app.version,
            requestCount
        };
    });

    // =============================================================================
    // Configuration Routes
    // =============================================================================

    server.get('/config', async (request, reply) => {
        server.logger.info('Configuration requested');
        return {
            app: server.config.app,
            features: server.config.features,
            providerNames: Object.keys(server.config.providers)
        };
    });

    server.get('/context', async (request, reply) => {
        const context = await buildContext(request, server.config);
        server.logger.debug('Context requested', { keys: Object.keys(context) });

        return {
            keys: Object.keys(context),
            app: context.app,
            auth: context.auth,
            tenant: context.tenant
        };
    });

    // =============================================================================
    // Provider Routes
    // =============================================================================

    interface ProviderParams {
        providerName: string;
    }

    server.get<{ Params: ProviderParams }>(
        '/providers/:providerName',
        async (request, reply) => {
            const { providerName } = request.params;
            server.logger.info('Provider requested', { provider: providerName });

            const providers = server.config.providers;
            if (!(providerName in providers)) {
                return reply.status(404).send({
                    error: 'Not Found',
                    message: `Provider '${providerName}' not found`
                });
            }

            const provider = providers[providerName];
            const context = await buildContext(request, server.config);
            const overwrites = provider.overwrite_from_context || {};

            // Resolve templates
            const resolvedOverwrites = resolveTemplates(overwrites, context);

            // Apply overwrites
            const resolved = applyOverwrites(provider, resolvedOverwrites);

            return {
                name: providerName,
                baseUrl: resolved.baseUrl,
                timeout: resolved.timeout,
                headers: resolved.headers,
                resolved: true
            };
        }
    );

    server.get<{ Params: ProviderParams }>(
        '/providers/:providerName/raw',
        async (request, reply) => {
            const { providerName } = request.params;

            const providers = server.config.providers;
            if (!(providerName in providers)) {
                return reply.status(404).send({
                    error: 'Not Found',
                    message: `Provider '${providerName}' not found`
                });
            }

            const provider = providers[providerName];

            return {
                name: providerName,
                baseUrl: provider.baseUrl,
                timeout: provider.timeout,
                headers: provider.headers,
                resolved: false
            };
        }
    );

    // =============================================================================
    // Demo Route - Shows Full Resolution
    // =============================================================================

    server.get('/demo/resolved-headers', async (request, reply) => {
        const context = await buildContext(request, server.config);

        const results: Record<string, any> = {};

        for (const [name, provider] of Object.entries(server.config.providers)) {
            const overwrites = provider.overwrite_from_context || {};
            const resolvedOverwrites = resolveTemplates(overwrites, context);
            const resolved = applyOverwrites(provider, resolvedOverwrites);

            results[name] = {
                originalHeaders: provider.headers,
                resolvedHeaders: resolved.headers
            };
        }

        return {
            context: {
                auth: context.auth,
                tenant: context.tenant
            },
            providers: results
        };
    });

    return server;
}

// =============================================================================
// Main
// =============================================================================

async function main(): Promise<void> {
    const server = await buildServer();
    const logger = server.logger;

    try {
        const address = await server.listen({ port: 3000, host: '0.0.0.0' });
        logger.info('Server started', { address, appName: server.config.app.name });

        console.log('\n' + '='.repeat(60));
        console.log('Fastify Example Server Running');
        console.log('='.repeat(60));
        console.log(`\nServer: ${address}`);
        console.log('\nEndpoints:');
        console.log('  GET /health              - Health check');
        console.log('  GET /config              - Configuration info');
        console.log('  GET /context             - Current resolution context');
        console.log('  GET /providers/:name     - Resolved provider config');
        console.log('  GET /providers/:name/raw - Raw provider config');
        console.log('  GET /demo/resolved-headers - Demo all resolved headers');
        console.log('\nTest with:');
        console.log('  curl http://localhost:3000/health');
        console.log('  curl -H "Authorization: Bearer my-token" -H "X-Tenant-Id: tenant-123" \\');
        console.log('       http://localhost:3000/providers/userApi');
        console.log('='.repeat(60));
    } catch (err) {
        logger.error('Failed to start server', { error: String(err) });
        process.exit(1);
    }
}

main();
