/**
 * Fastify Integration Example for Runtime Template Resolver
 *
 * This example demonstrates:
 * - Plugin-based resolver integration
 * - Request-scoped template resolution
 * - Configuration template resolution
 * - Email/notification templating
 * - API response templating
 */

import Fastify, { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import fastifyTemplateResolver from '../../src/integrations/fastify-plugin.js';
import { TemplateResolver, MissingStrategy } from '../../src/index.js';

// =============================================================================
// Application Configuration (simulated app-yaml style config)
// =============================================================================
const APP_CONFIG = {
    app: {
        name: 'Template Resolver Demo',
        version: '1.0.0'
    },
    database: {
        url: 'postgres://{{db.host}}:{{db.port}}/{{db.name}}',
        poolSize: 10
    },
    email: {
        templates: {
            welcome: 'Welcome to {{app.name}}, {{user.name}}!',
            order_confirmation: 'Your order #{{order.id}} for ${{order.total}} has been confirmed.',
            password_reset: 'Click here to reset your password: {{reset_url}}'
        }
    },
    api: {
        baseUrl: 'https://{{api.domain}}/v{{api.version}}'
    }
};

// Runtime context that would come from environment/secrets
const RUNTIME_CONTEXT = {
    db: { host: 'localhost', port: '5432', name: 'demo_db' },
    api: { domain: 'api.example.com', version: '2' },
    app: { name: 'Template Resolver Demo' }
};

// =============================================================================
// Type Definitions
// =============================================================================
interface ResolveBody {
    template: string;
    context: Record<string, unknown>;
}

interface EmailBody {
    template_name: string;
    recipient: string;
    context: Record<string, unknown>;
}

// Augment FastifyInstance to include our resolved config
declare module 'fastify' {
    interface FastifyInstance {
        resolvedConfig: typeof APP_CONFIG;
    }
}

// =============================================================================
// Application Setup
// =============================================================================
async function buildServer(): Promise<FastifyInstance> {
    const server = Fastify({
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

    // Pre-resolve static configuration at startup
    const resolver = new TemplateResolver();
    const resolvedConfig = resolver.resolveObject(APP_CONFIG, RUNTIME_CONTEXT) as typeof APP_CONFIG;

    // Decorate server with resolved config
    server.decorate('resolvedConfig', resolvedConfig);

    // Register the template resolver plugin
    await server.register(fastifyTemplateResolver, {
        missingStrategy: MissingStrategy.EMPTY
    });

    // =============================================================================
    // Routes
    // =============================================================================

    // Health check endpoint
    server.get('/health', async (request, reply) => {
        return {
            status: 'ok',
            appName: server.resolvedConfig.app.name,
            version: server.resolvedConfig.app.version
        };
    });

    // Get resolved configuration
    server.get('/config', async (request, reply) => {
        return {
            databaseUrl: server.resolvedConfig.database.url,
            apiBaseUrl: server.resolvedConfig.api.baseUrl,
            poolSize: server.resolvedConfig.database.poolSize
        };
    });

    // Resolve a template with provided context
    server.post<{ Body: ResolveBody }>('/resolve', async (request, reply) => {
        const { template, context } = request.body;
        const resolved = request.resolveTemplate(template, context);
        return {
            original: template,
            resolved
        };
    });

    // Resolve templates within a nested object
    server.post('/resolve-object', async (request, reply) => {
        const data = request.body as Record<string, unknown>;

        // Build user context from request
        const userContext = {
            user: {
                id: 'user-123',
                name: 'Demo User',
                email: 'demo@example.com'
            },
            request: {
                ip: request.ip,
                path: request.url
            }
        };

        // Resolve each string in the object
        const innerResolver = new TemplateResolver();
        const resolved = innerResolver.resolveObject(data, userContext);

        return {
            original: data,
            resolved,
            contextUsed: userContext
        };
    });

    // Preview an email using a named template
    server.post<{ Body: EmailBody }>('/email/preview', async (request, reply) => {
        const { template_name, recipient, context } = request.body;
        const templates = server.resolvedConfig.email.templates as Record<string, string>;

        if (!(template_name in templates)) {
            reply.code(400);
            return {
                error: `Unknown template: ${template_name}. Available: ${Object.keys(templates).join(', ')}`
            };
        }

        // Merge app context with request context
        const fullContext = { ...RUNTIME_CONTEXT, ...context };
        const body = request.resolveTemplate(templates[template_name], fullContext);

        // Generate subject based on template name
        const subjects: Record<string, string> = {
            welcome: 'Welcome to {{app.name}}!',
            order_confirmation: 'Order #{{order.id}} Confirmed',
            password_reset: 'Password Reset Request'
        };
        const subject = request.resolveTemplate(subjects[template_name] || 'Notification', fullContext);

        return {
            to: recipient,
            subject,
            body
        };
    });

    // Simple demo endpoint
    server.get<{ Querystring: { name?: string } }>('/demo/greeting', async (request, reply) => {
        const name = request.query.name || 'World';
        const template = 'Hello, {{name}}! Welcome to our API.';
        const result = request.resolveTemplate(template, { name });
        return { message: result };
    });

    // Demo endpoint showing user context injection
    server.get('/demo/user-info', async (request, reply) => {
        const userContext = {
            user: { name: 'Demo User', email: 'demo@example.com' },
            request: { ip: request.ip }
        };
        const template = 'User {{user.name}} ({{user.email}}) accessing from {{request.ip}}';
        const result = request.resolveTemplate(template, userContext);
        return { message: result, context: userContext };
    });

    // Batch resolution demo
    server.post('/demo/batch', async (request, reply) => {
        const { templates, context } = request.body as {
            templates: string[];
            context: Record<string, unknown>;
        };

        const innerResolver = new TemplateResolver();
        const results = templates.map(t => innerResolver.resolve(t, context));

        return {
            count: templates.length,
            results
        };
    });

    return server;
}

// =============================================================================
// Main Entry Point
// =============================================================================
async function main(): Promise<void> {
    const server = await buildServer();

    // Startup logging
    server.addHook('onReady', async () => {
        console.log('='.repeat(60));
        console.log('Fastify Template Resolver Demo - Starting');
        console.log('='.repeat(60));
        console.log(`Database URL: ${server.resolvedConfig.database.url}`);
        console.log(`API Base URL: ${server.resolvedConfig.api.baseUrl}`);
        console.log('='.repeat(60));
    });

    try {
        const address = await server.listen({ port: 3000, host: '0.0.0.0' });
        console.log(`Server listening at ${address}`);
        console.log(`API docs: Try GET /health, POST /resolve, etc.`);
    } catch (err) {
        server.log.error(err);
        process.exit(1);
    }
}

main();
