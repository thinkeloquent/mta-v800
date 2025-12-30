/**
 * Fastify integration tests for vault_file.
 *
 * Tests cover:
 * - Plugin registration
 * - EnvStore initialization via Fastify startup
 * - Request state isolation
 * - Lifecycle hooks
 * - Error handling during startup
 */
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import Fastify from 'fastify';
import { EnvStore } from '../src/env-store';
import { createTempEnvFile, cleanupTempFile } from './helpers/test-utils';
describe('Fastify Integration', () => {
    let server;
    let tempFilePath = null;
    beforeEach(() => {
        // Reset EnvStore singleton
        EnvStore.instance = undefined;
    });
    afterEach(async () => {
        if (server) {
            await server.close();
        }
        if (tempFilePath) {
            cleanupTempFile(tempFilePath);
            tempFilePath = null;
        }
    });
    /**
     * Create a test server with vault_file integration.
     */
    async function createTestServer(envPath) {
        const fastify = Fastify({ logger: false });
        // Register vault_file plugin
        const path = envPath || '/nonexistent/.env';
        const result = await EnvStore.onStartup(path);
        fastify.decorate('vaultLoaded', result.totalVarsLoaded);
        // Add health endpoint
        fastify.get('/health', async () => ({
            status: 'ok',
            vaultInitialized: EnvStore.isInitialized(),
        }));
        // Add secret endpoint
        fastify.get('/secret/:key', async (request) => {
            const value = EnvStore.get(request.params.key);
            return {
                key: request.params.key,
                exists: value !== undefined,
                masked: value !== undefined ? '***' : null,
            };
        });
        // Add secret value endpoint (for testing only)
        fastify.get('/secret-value/:key', async (request) => ({
            key: request.params.key,
            value: EnvStore.get(request.params.key),
        }));
        await fastify.ready();
        return fastify;
    }
    // =========================================================================
    // Health Endpoint Tests
    // =========================================================================
    describe('Health Endpoint', () => {
        it('should return 200 OK', async () => {
            server = await createTestServer();
            const response = await server.inject({
                method: 'GET',
                url: '/health',
            });
            expect(response.statusCode).toBe(200);
            expect(response.json().status).toBe('ok');
        });
        it('should show vault initialized state', async () => {
            tempFilePath = createTempEnvFile('KEY=value');
            server = await createTestServer(tempFilePath);
            const response = await server.inject({
                method: 'GET',
                url: '/health',
            });
            expect(response.json().vaultInitialized).toBe(true);
        });
    });
    // =========================================================================
    // Secret Endpoint Tests
    // =========================================================================
    describe('Secret Endpoint', () => {
        it('should return exists=true for existing secret', async () => {
            tempFilePath = createTempEnvFile('TEST_API_KEY=test-secret-123');
            server = await createTestServer(tempFilePath);
            const response = await server.inject({
                method: 'GET',
                url: '/secret/TEST_API_KEY',
            });
            const data = response.json();
            expect(data.key).toBe('TEST_API_KEY');
            expect(data.exists).toBe(true);
            expect(data.masked).toBe('***');
        });
        it('should return exists=false for missing secret', async () => {
            server = await createTestServer();
            const response = await server.inject({
                method: 'GET',
                url: '/secret/NONEXISTENT_KEY',
            });
            const data = response.json();
            expect(data.key).toBe('NONEXISTENT_KEY');
            expect(data.exists).toBe(false);
        });
        it('should return actual secret value', async () => {
            tempFilePath = createTempEnvFile('TEST_API_KEY=test-secret-123');
            server = await createTestServer(tempFilePath);
            const response = await server.inject({
                method: 'GET',
                url: '/secret-value/TEST_API_KEY',
            });
            expect(response.json().value).toBe('test-secret-123');
        });
    });
    // =========================================================================
    // Lifecycle Tests
    // =========================================================================
    describe('Lifecycle Hooks', () => {
        it('should initialize EnvStore on startup', async () => {
            tempFilePath = createTempEnvFile('KEY=value');
            server = await createTestServer(tempFilePath);
            expect(EnvStore.isInitialized()).toBe(true);
        });
        it('should load vars from env file', async () => {
            tempFilePath = createTempEnvFile('TEST_KEY=test_value\nANOTHER_KEY=another_value');
            server = await createTestServer(tempFilePath);
            expect(EnvStore.get('TEST_KEY')).toBe('test_value');
            expect(EnvStore.get('ANOTHER_KEY')).toBe('another_value');
        });
        it('should execute onClose hooks', async () => {
            let closeCalled = false;
            server = Fastify({ logger: false });
            server.addHook('onClose', async () => {
                closeCalled = true;
            });
            await server.ready();
            await server.close();
            expect(closeCalled).toBe(true);
        });
        it('should execute onReady hooks', async () => {
            let readyCalled = false;
            server = Fastify({ logger: false });
            server.addHook('onReady', async () => {
                readyCalled = true;
            });
            await server.ready();
            expect(readyCalled).toBe(true);
        });
    });
    // =========================================================================
    // Server Decorators Tests
    // =========================================================================
    describe('Server Decorators', () => {
        it('should decorate server with vault loaded count', async () => {
            tempFilePath = createTempEnvFile('KEY=value');
            server = await createTestServer(tempFilePath);
            expect(server.vaultLoaded).toBeGreaterThan(0);
        });
    });
    // =========================================================================
    // Request Isolation Tests
    // =========================================================================
    describe('Request Isolation', () => {
        it('should return same env values across multiple requests', async () => {
            tempFilePath = createTempEnvFile('TEST_KEY=test_value');
            server = await createTestServer(tempFilePath);
            const response1 = await server.inject({
                method: 'GET',
                url: '/secret-value/TEST_KEY',
            });
            const response2 = await server.inject({
                method: 'GET',
                url: '/secret-value/TEST_KEY',
            });
            expect(response1.json().value).toBe(response2.json().value);
        });
        it('should handle concurrent requests', async () => {
            tempFilePath = createTempEnvFile('KEY1=value1\nKEY2=value2');
            server = await createTestServer(tempFilePath);
            const [res1, res2, res3] = await Promise.all([
                server.inject({ method: 'GET', url: '/secret/KEY1' }),
                server.inject({ method: 'GET', url: '/secret/KEY2' }),
                server.inject({ method: 'GET', url: '/secret/NONEXISTENT' }),
            ]);
            expect(res1.json().exists).toBe(true);
            expect(res2.json().exists).toBe(true);
            expect(res3.json().exists).toBe(false);
        });
    });
    // =========================================================================
    // Error Handling Tests
    // =========================================================================
    describe('Error Handling', () => {
        it('should start with missing env file', async () => {
            server = await createTestServer('/nonexistent/.env');
            const response = await server.inject({
                method: 'GET',
                url: '/health',
            });
            expect(response.statusCode).toBe(200);
        });
        it('should handle plugin registration errors gracefully', async () => {
            server = Fastify({ logger: false });
            // Register a plugin that throws
            server.register(async () => {
                await EnvStore.onStartup('/nonexistent/.env');
                // This should not throw, just warn
            });
            // Should not throw
            await expect(server.ready()).resolves.toBeDefined();
        });
    });
    // =========================================================================
    // inject() Method Tests
    // =========================================================================
    describe('inject() Method', () => {
        it('should support GET requests', async () => {
            server = await createTestServer();
            const response = await server.inject({
                method: 'GET',
                url: '/health',
            });
            expect(response.statusCode).toBe(200);
        });
        it('should support custom headers', async () => {
            server = await createTestServer();
            const response = await server.inject({
                method: 'GET',
                url: '/health',
                headers: {
                    'X-Custom-Header': 'test-value',
                },
            });
            expect(response.statusCode).toBe(200);
        });
        it('should parse JSON response', async () => {
            server = await createTestServer();
            const response = await server.inject({
                method: 'GET',
                url: '/health',
            });
            const json = response.json();
            expect(json).toHaveProperty('status');
            expect(json).toHaveProperty('vaultInitialized');
        });
    });
});
//# sourceMappingURL=api.test.js.map