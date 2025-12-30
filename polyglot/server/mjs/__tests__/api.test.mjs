/**
 * Fastify integration tests for server.
 *
 * Tests cover:
 * - Health endpoint
 * - Root endpoint
 * - Request state isolation
 * - inject() testing without network
 */
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import Fastify from 'fastify';
import { init, start, stop } from '../src/server.mjs';

describe('Fastify API Integration', () => {
    // =========================================================================
    // Test Server Setup
    // =========================================================================

    /**
     * Create a test server with routes.
     */
    async function createTestServer(config = {}) {
        const defaultConfig = {
            title: 'Test API',
            host: '127.0.0.1',
            port: 0,
            logger: false,
            initial_state: { user: 'test', role: 'tester' },
            ...config,
        };

        const server = init({ ...defaultConfig, logger: false });

        // Register routes
        server.get('/', async (request) => ({
            status: 'ok',
            state: request.state,
        }));

        server.get('/health', async (request) => ({
            status: 'ok',
            state: request.state,
        }));

        server.get('/echo/:message', async (request) => ({
            message: request.params.message,
            user: request.state?.user,
        }));

        await start(server, defaultConfig);

        return server;
    }

    // =========================================================================
    // Health Endpoint Tests
    // =========================================================================

    describe('Health Endpoint', () => {
        let server;

        beforeEach(async () => {
            server = await createTestServer();
        });

        afterEach(async () => {
            await server.close();
        });

        it('should return 200 OK', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/health',
            });

            expect(response.statusCode).toBe(200);
            expect(response.json().status).toBe('ok');
        });

        it('should include request state', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/health',
            });

            const body = response.json();
            expect(body.state).toBeDefined();
            expect(body.state.user).toBe('test');
            expect(body.state.role).toBe('tester');
        });
    });

    // =========================================================================
    // Root Endpoint Tests
    // =========================================================================

    describe('Root Endpoint', () => {
        let server;

        beforeEach(async () => {
            server = await createTestServer();
        });

        afterEach(async () => {
            await server.close();
        });

        it('should return 200 OK', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/',
            });

            expect(response.statusCode).toBe(200);
            expect(response.json().status).toBe('ok');
        });

        it('should include request state', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/',
            });

            const body = response.json();
            expect(body.state.user).toBe('test');
        });
    });

    // =========================================================================
    // Echo Endpoint Tests
    // =========================================================================

    describe('Echo Endpoint', () => {
        let server;

        beforeEach(async () => {
            server = await createTestServer();
        });

        afterEach(async () => {
            await server.close();
        });

        it('should return the message', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/echo/hello',
            });

            expect(response.statusCode).toBe(200);
            expect(response.json().message).toBe('hello');
        });

        it('should include user from state', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/echo/test',
            });

            const body = response.json();
            expect(body.user).toBe('test');
        });
    });

    // =========================================================================
    // Request State Isolation Tests
    // =========================================================================

    describe('Request State Isolation', () => {
        it('should isolate state between requests', async () => {
            const defaultConfig = {
                title: 'Test API',
                host: '127.0.0.1',
                port: 0,
                logger: false,
                initial_state: { user: 'test', role: 'tester' },
            };

            const server = init({ ...defaultConfig, logger: false });

            // Add routes BEFORE start
            server.get('/mutate', async (request) => {
                request.state.user = 'mutated';
                return { user: request.state.user };
            });

            server.get('/health', async (request) => ({
                status: 'ok',
                state: request.state,
            }));

            await start(server, defaultConfig);

            // Mutate state
            const mutateResponse = await server.inject({
                method: 'GET',
                url: '/mutate',
            });
            expect(mutateResponse.json().user).toBe('mutated');

            // Check that next request has fresh state
            const checkResponse = await server.inject({
                method: 'GET',
                url: '/health',
            });
            expect(checkResponse.json().state.user).toBe('test');

            await server.close();
        });

        it('should give each request fresh state copy', async () => {
            const server = await createTestServer();

            const response1 = await server.inject({
                method: 'GET',
                url: '/health',
            });
            const response2 = await server.inject({
                method: 'GET',
                url: '/health',
            });

            // States should be equal (both fresh copies)
            expect(response1.json().state).toEqual(response2.json().state);

            await server.close();
        });

        it('should handle concurrent requests', async () => {
            const server = await createTestServer();

            const responses = await Promise.all([
                server.inject({ method: 'GET', url: '/health' }),
                server.inject({ method: 'GET', url: '/' }),
                server.inject({ method: 'GET', url: '/echo/test' }),
            ]);

            expect(responses[0].json().state.user).toBe('test');
            expect(responses[1].json().state.user).toBe('test');
            expect(responses[2].json().user).toBe('test');

            await server.close();
        });
    });

    // =========================================================================
    // Server Without Initial State
    // =========================================================================

    describe('Server Without Initial State', () => {
        it('should work when initial_state is not configured', async () => {
            const server = init({ title: 'No State', logger: false });

            server.get('/health', async () => ({
                status: 'ok',
            }));

            await server.ready();

            const response = await server.inject({
                method: 'GET',
                url: '/health',
            });

            expect(response.statusCode).toBe(200);
            expect(response.json().status).toBe('ok');

            await server.close();
        });
    });

    // =========================================================================
    // Server Decorators Tests
    // =========================================================================

    describe('Server Decorators', () => {
        it('should decorate server with config', async () => {
            const config = { title: 'Custom API', logger: false };
            const server = await createTestServer(config);

            expect(server._config.title).toBe('Custom API');

            await server.close();
        });

        it('should decorate server with initialState', async () => {
            const server = await createTestServer({
                initial_state: { custom: 'value' },
            });

            expect(server.initialState).toBeDefined();
            expect(server.initialState.custom).toBe('value');

            await server.close();
        });
    });

    // =========================================================================
    // Error Handling Tests
    // =========================================================================

    describe('Error Handling', () => {
        it('should return 404 for unknown routes', async () => {
            const server = await createTestServer();

            const response = await server.inject({
                method: 'GET',
                url: '/nonexistent',
            });

            expect(response.statusCode).toBe(404);

            await server.close();
        });

        it('should handle server close gracefully', async () => {
            const server = await createTestServer();

            // Server should be listening
            expect(server.addresses().length).toBeGreaterThan(0);

            // Should not throw
            await stop(server, { title: 'Test' });

            // Server should be closed - addresses returns empty array
            expect(server.addresses()).toEqual([]);
        });
    });

    // =========================================================================
    // Lifecycle Hooks Tests
    // =========================================================================

    describe('Lifecycle Hooks', () => {
        it('should execute onReady hooks', async () => {
            const server = init({ title: 'Test', logger: false });
            let hookCalled = false;

            server.addHook('onReady', async () => {
                hookCalled = true;
            });

            await server.ready();
            expect(hookCalled).toBe(true);

            await server.close();
        });

        it('should execute onClose hooks', async () => {
            const server = init({ title: 'Test', logger: false });
            let hookCalled = false;

            server.addHook('onClose', async () => {
                hookCalled = true;
            });

            await server.ready();
            await server.close();

            expect(hookCalled).toBe(true);
        });
    });

    // =========================================================================
    // inject() Helper Tests
    // =========================================================================

    describe('inject() Helper', () => {
        it('should support different HTTP methods', async () => {
            const config = {
                title: 'Test API',
                host: '127.0.0.1',
                port: 0,
                logger: false,
            };

            const server = init({ ...config, logger: false });

            // Add route BEFORE start
            server.post('/data', async (request) => ({
                received: true,
                body: request.body,
            }));

            await start(server, config);

            const response = await server.inject({
                method: 'POST',
                url: '/data',
                payload: { test: 'data' },
            });

            expect(response.statusCode).toBe(200);
            expect(response.json().received).toBe(true);

            await server.close();
        });

        it('should support custom headers', async () => {
            const config = {
                title: 'Test API',
                host: '127.0.0.1',
                port: 0,
                logger: false,
            };

            const server = init({ ...config, logger: false });

            // Add route BEFORE start
            server.get('/headers', async (request) => ({
                customHeader: request.headers['x-custom'],
            }));

            await start(server, config);

            const response = await server.inject({
                method: 'GET',
                url: '/headers',
                headers: { 'x-custom': 'test-value' },
            });

            expect(response.json().customHeader).toBe('test-value');

            await server.close();
        });

        it('should support query parameters', async () => {
            const config = {
                title: 'Test API',
                host: '127.0.0.1',
                port: 0,
                logger: false,
            };

            const server = init({ ...config, logger: false });

            // Add route BEFORE start
            server.get('/query', async (request) => ({
                name: request.query.name,
            }));

            await start(server, config);

            const response = await server.inject({
                method: 'GET',
                url: '/query?name=test',
            });

            expect(response.json().name).toBe('test');

            await server.close();
        });
    });
});
