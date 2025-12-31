/**
 * Fastify integration tests.
 *
 * Tests cover:
 * - Plugin registration
 * - Request decorator
 * - Template resolution in request context
 * - Lifecycle hooks
 */
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import Fastify, { FastifyInstance } from 'fastify';
import fastifyTemplateResolver from '../../src/integrations/fastify-plugin.js';
import { MissingStrategy } from '../../src/interfaces.js';

describe('Fastify Plugin Integration', () => {
    let server: FastifyInstance;

    beforeEach(async () => {
        server = Fastify({ logger: false });
    });

    afterEach(async () => {
        await server.close();
    });

    describe('Plugin Registration', () => {
        it('should register plugin successfully', async () => {
            await server.register(fastifyTemplateResolver);
            await server.ready();
            expect(server).toBeDefined();
        });

        it('should register plugin with options', async () => {
            await server.register(fastifyTemplateResolver, {
                missingStrategy: MissingStrategy.KEEP
            });
            await server.ready();
            expect(server).toBeDefined();
        });
    });

    describe('Request Decorator', () => {
        it('should decorate request with resolveTemplate', async () => {
            await server.register(fastifyTemplateResolver);

            let hasDecorator = false;
            server.get('/test', async (request) => {
                hasDecorator = typeof request.resolveTemplate === 'function';
                return { hasDecorator };
            });

            await server.ready();
            const response = await server.inject({
                method: 'GET',
                url: '/test'
            });

            expect(response.statusCode).toBe(200);
            expect(response.json().hasDecorator).toBe(true);
        });

        it('should resolve template via decorator', async () => {
            await server.register(fastifyTemplateResolver);

            server.get('/resolve', async (request) => {
                const result = request.resolveTemplate('Hello {{name}}!', { name: 'World' });
                return { result };
            });

            await server.ready();
            const response = await server.inject({
                method: 'GET',
                url: '/resolve'
            });

            expect(response.statusCode).toBe(200);
            expect(response.json().result).toBe('Hello World!');
        });
    });

    describe('Template Resolution', () => {
        it('should resolve simple placeholder', async () => {
            await server.register(fastifyTemplateResolver);

            server.get('/simple', async (request) => {
                return { result: request.resolveTemplate('{{name}}', { name: 'Test' }) };
            });

            await server.ready();
            const response = await server.inject({ method: 'GET', url: '/simple' });
            expect(response.json().result).toBe('Test');
        });

        it('should resolve nested paths', async () => {
            await server.register(fastifyTemplateResolver);

            server.get('/nested', async (request) => {
                const context = { user: { profile: { name: 'Alice' } } };
                return { result: request.resolveTemplate('{{user.profile.name}}', context) };
            });

            await server.ready();
            const response = await server.inject({ method: 'GET', url: '/nested' });
            expect(response.json().result).toBe('Alice');
        });

        it('should handle default values', async () => {
            await server.register(fastifyTemplateResolver);

            server.get('/default', async (request) => {
                return { result: request.resolveTemplate('{{missing | "default"}}', {}) };
            });

            await server.ready();
            const response = await server.inject({ method: 'GET', url: '/default' });
            expect(response.json().result).toBe('default');
        });

        it('should handle missing values with EMPTY strategy', async () => {
            await server.register(fastifyTemplateResolver);

            server.get('/missing', async (request) => {
                return { result: request.resolveTemplate('Value: {{missing}}', {}) };
            });

            await server.ready();
            const response = await server.inject({ method: 'GET', url: '/missing' });
            expect(response.json().result).toBe('Value: ');
        });
    });

    describe('Plugin Options', () => {
        it('should respect KEEP missing strategy from plugin options', async () => {
            await server.register(fastifyTemplateResolver, {
                missingStrategy: MissingStrategy.KEEP
            });

            server.get('/test', async (request) => {
                return { result: request.resolveTemplate('{{missing}}', {}) };
            });

            await server.ready();
            const response = await server.inject({ method: 'GET', url: '/test' });
            expect(response.json().result).toBe('{{missing}}');
        });

        it('should allow request-level options to override plugin options', async () => {
            await server.register(fastifyTemplateResolver, {
                missingStrategy: MissingStrategy.KEEP
            });

            server.get('/test', async (request) => {
                return {
                    result: request.resolveTemplate('{{missing}}', {}, {
                        missingStrategy: MissingStrategy.EMPTY
                    })
                };
            });

            await server.ready();
            const response = await server.inject({ method: 'GET', url: '/test' });
            expect(response.json().result).toBe('');
        });
    });

    describe('Error Handling', () => {
        it('should handle private attribute access gracefully', async () => {
            await server.register(fastifyTemplateResolver);

            server.get('/private', async (request) => {
                return { result: request.resolveTemplate('{{_private}}', {}) };
            });

            await server.ready();
            const response = await server.inject({ method: 'GET', url: '/private' });
            expect(response.statusCode).toBe(200);
            expect(response.json().result).toBe('{{_private}}');
        });
    });

    describe('Request Isolation', () => {
        it('should isolate context between requests', async () => {
            await server.register(fastifyTemplateResolver);

            server.get('/isolated', async (request, reply) => {
                const id = request.query as any;
                return { result: request.resolveTemplate('ID: {{id}}', { id: id.id || 'none' }) };
            });

            await server.ready();

            const response1 = await server.inject({
                method: 'GET',
                url: '/isolated?id=first'
            });
            const response2 = await server.inject({
                method: 'GET',
                url: '/isolated?id=second'
            });

            expect(response1.json().result).toBe('ID: first');
            expect(response2.json().result).toBe('ID: second');
        });
    });

    describe('Lifecycle Hooks', () => {
        it('should work with onRequest hook', async () => {
            await server.register(fastifyTemplateResolver);

            server.addHook('onRequest', async (request) => {
                (request as any).customData = { name: 'FromHook' };
            });

            server.get('/hook', async (request) => {
                const data = (request as any).customData;
                return { result: request.resolveTemplate('{{name}}', data) };
            });

            await server.ready();
            const response = await server.inject({ method: 'GET', url: '/hook' });
            expect(response.json().result).toBe('FromHook');
        });
    });
});

describe('Fastify Plugin Health Check Pattern', () => {
    it('should work in health endpoint pattern', async () => {
        const server = Fastify({ logger: false });
        await server.register(fastifyTemplateResolver);

        server.get('/health', async (request) => {
            return {
                status: 'ok',
                message: request.resolveTemplate('Server is {{status}}', { status: 'healthy' })
            };
        });

        await server.ready();
        const response = await server.inject({ method: 'GET', url: '/health' });

        expect(response.statusCode).toBe(200);
        expect(response.json().status).toBe('ok');
        expect(response.json().message).toBe('Server is healthy');

        await server.close();
    });
});
