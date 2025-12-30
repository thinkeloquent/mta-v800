/**
 * Fastify integration tests for app-yaml-static-config.
 *
 * Tests verify that the configuration module integrates correctly
 * with Fastify applications, including:
 * - Configuration access from route handlers
 * - Request state isolation
 * - Plugin integration
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Fastify from 'fastify';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { AppYamlConfig } from '../dist/core.js';
import { AppYamlConfigSDK } from '../dist/sdk.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, '..', '..', '__fixtures__');

// Helper to reset singleton
function resetSingleton() {
    AppYamlConfig._instance = null;
}

/**
 * Create a test Fastify server with configuration.
 */
async function createTestServer() {
    // Initialize configuration
    const options = {
        files: [path.join(FIXTURES_DIR, 'base.yaml')],
        configDir: FIXTURES_DIR,
    };
    await AppYamlConfig.initialize(options);
    const config = AppYamlConfig.getInstance();
    const sdk = new AppYamlConfigSDK(config);

    // Create Fastify instance
    const fastify = Fastify({ logger: false });

    // Decorate server with config
    fastify.decorate('config', config);
    fastify.decorate('sdk', sdk);

    // Register routes
    fastify.get('/health', async (request, reply) => {
        return {
            status: 'ok',
            app_name: fastify.config.getNested(['app', 'name']),
        };
    });

    fastify.get('/config', async (request, reply) => {
        return fastify.sdk.getAll();
    });

    fastify.get('/config/:key', async (request, reply) => {
        const { key } = request.params;
        return {
            key,
            value: fastify.sdk.get(key),
        };
    });

    fastify.get('/providers', async (request, reply) => {
        return {
            providers: fastify.sdk.listProviders(),
        };
    });

    fastify.get('/services', async (request, reply) => {
        return {
            services: fastify.sdk.listServices(),
        };
    });

    fastify.get('/storages', async (request, reply) => {
        return {
            storages: fastify.sdk.listStorages(),
        };
    });

    await fastify.ready();
    return fastify;
}

describe('Fastify Integration', () => {
    let server;

    beforeEach(async () => {
        resetSingleton();
        server = await createTestServer();
    });

    afterEach(async () => {
        await server.close();
        resetSingleton();
    });

    describe('Health Endpoint', () => {
        it('should return 200 OK', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/health',
            });

            expect(response.statusCode).toBe(200);
            expect(response.json().status).toBe('ok');
        });

        it('should include app name from config', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/health',
            });

            const body = response.json();
            expect(body.app_name).toBe('test-app');
        });
    });

    describe('Config Endpoint', () => {
        it('should return full configuration', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/config',
            });

            expect(response.statusCode).toBe(200);
            const body = response.json();
            expect(body.app).toBeDefined();
            expect(body.providers).toBeDefined();
            expect(body.services).toBeDefined();
        });

        it('should return specific config key', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/config/app',
            });

            expect(response.statusCode).toBe(200);
            const body = response.json();
            expect(body.key).toBe('app');
            expect(body.value.name).toBe('test-app');
        });

        it('should return null for missing key', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/config/nonexistent',
            });

            expect(response.statusCode).toBe(200);
            const body = response.json();
            expect(body.key).toBe('nonexistent');
            expect(body.value).toBeUndefined();
        });
    });

    describe('Providers Endpoint', () => {
        it('should return list of providers', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/providers',
            });

            expect(response.statusCode).toBe(200);
            const body = response.json();
            expect(Array.isArray(body.providers)).toBe(true);
            expect(body.providers).toContain('anthropic');
            expect(body.providers).toContain('openai');
        });
    });

    describe('Services Endpoint', () => {
        it('should return list of services', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/services',
            });

            expect(response.statusCode).toBe(200);
            const body = response.json();
            expect(Array.isArray(body.services)).toBe(true);
            expect(body.services).toContain('database');
            expect(body.services).toContain('cache');
        });
    });

    describe('Storages Endpoint', () => {
        it('should return list of storages', async () => {
            const response = await server.inject({
                method: 'GET',
                url: '/storages',
            });

            expect(response.statusCode).toBe(200);
            const body = response.json();
            expect(Array.isArray(body.storages)).toBe(true);
            expect(body.storages).toContain('local');
            expect(body.storages).toContain('s3');
        });
    });

    describe('Request Isolation', () => {
        it('should use same config across requests', async () => {
            const response1 = await server.inject({
                method: 'GET',
                url: '/config/app',
            });
            const response2 = await server.inject({
                method: 'GET',
                url: '/config/app',
            });

            expect(response1.json()).toEqual(response2.json());
        });

        it('should maintain config immutability', async () => {
            // Get initial app name
            const response1 = await server.inject({
                method: 'GET',
                url: '/health',
            });
            const appName1 = response1.json().app_name;

            // Make several requests
            for (let i = 0; i < 5; i++) {
                await server.inject({ method: 'GET', url: '/providers' });
                await server.inject({ method: 'GET', url: '/services' });
            }

            // App name should be unchanged
            const response2 = await server.inject({
                method: 'GET',
                url: '/health',
            });
            const appName2 = response2.json().app_name;

            expect(appName1).toBe(appName2);
        });
    });

    describe('Server Decorators', () => {
        it('should decorate server with config', async () => {
            expect(server.config).toBeDefined();
            expect(server.config).toBeInstanceOf(AppYamlConfig);
        });

        it('should decorate server with sdk', async () => {
            expect(server.sdk).toBeDefined();
            expect(server.sdk).toBeInstanceOf(AppYamlConfigSDK);
        });
    });

    describe('Lifecycle Hooks', () => {
        it('should execute onReady hook', async () => {
            let hookCalled = false;

            // Create new server with hook
            resetSingleton();
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);

            const testServer = Fastify({ logger: false });
            testServer.addHook('onReady', async () => {
                hookCalled = true;
            });

            await testServer.ready();

            expect(hookCalled).toBe(true);

            await testServer.close();
        });

        it('should execute onClose hook', async () => {
            let shutdownCalled = false;

            // Create new server with hook
            resetSingleton();
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);

            const testServer = Fastify({ logger: false });
            testServer.addHook('onClose', async () => {
                shutdownCalled = true;
            });

            await testServer.ready();
            await testServer.close();

            expect(shutdownCalled).toBe(true);
        });
    });
});
