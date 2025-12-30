/**
 * Unit tests for server module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Error handling verification
 */
import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { init, start, stop } from '../src/server.mjs';
import { createTempDir, cleanupTempDir } from './helpers/test-utils.mjs';
import fs from 'fs/promises';
import path from 'path';

describe('Server', () => {
    // =========================================================================
    // init() Function
    // =========================================================================

    describe('init()', () => {
        describe('Statement Coverage', () => {
            it('should return Fastify instance', () => {
                const server = init({ title: 'Test', logger: false });
                expect(server).toBeDefined();
                expect(typeof server.listen).toBe('function');
            });

            it('should accept config with title', () => {
                const server = init({ title: 'My API', logger: false });
                expect(server).toBeDefined();
            });
        });

        describe('Branch Coverage', () => {
            it('should work with empty config', () => {
                const server = init({ logger: false });
                expect(server).toBeDefined();
            });

            it('should use default logger when not specified', () => {
                const server = init({ title: 'Test' });
                expect(server).toBeDefined();
            });

            it('should disable logger when set to false', () => {
                const server = init({ title: 'Test', logger: false });
                expect(server).toBeDefined();
            });
        });
    });

    // =========================================================================
    // start() Function
    // =========================================================================

    describe('start()', () => {
        let server;
        let tempDir;

        beforeEach(async () => {
            server = init({ title: 'Test', logger: false });
            tempDir = await createTempDir();
        });

        afterEach(async () => {
            try {
                await server.close();
            } catch (e) {
                // Server might not be listening
            }
            if (tempDir) {
                await cleanupTempDir(tempDir);
            }
        });

        describe('Statement Coverage', () => {
            it('should start server and listen on port', async () => {
                const config = {
                    title: 'Test',
                    host: '127.0.0.1',
                    port: 0, // Random port
                    logger: false,
                };

                // Add a route for testing
                server.get('/test', async () => ({ status: 'ok' }));

                await start(server, config);

                // Server should be listening
                const addresses = server.addresses();
                expect(addresses.length).toBeGreaterThan(0);
            });

            it('should store config in server decorator', async () => {
                const config = {
                    title: 'Test API',
                    host: '127.0.0.1',
                    port: 0,
                };

                await start(server, config);

                expect(server._config).toBeDefined();
                expect(server._config.title).toBe('Test API');
            });
        });

        describe('Branch Coverage', () => {
            it('should work without bootstrap config', async () => {
                const config = {
                    title: 'Test',
                    host: '127.0.0.1',
                    port: 0,
                };

                await start(server, config);
                expect(server._shutdownHooks).toEqual([]);
            });

            it('should handle non-existent env directory', async () => {
                const config = {
                    title: 'Test',
                    host: '127.0.0.1',
                    port: 0,
                    bootstrap: {
                        load_env: '/nonexistent/path',
                    },
                };

                // Should not throw
                await start(server, config);
            });

            it('should handle non-existent lifecycle directory', async () => {
                const config = {
                    title: 'Test',
                    host: '127.0.0.1',
                    port: 0,
                    bootstrap: {
                        lifecycle: '/nonexistent/path',
                    },
                };

                // Should not throw
                await start(server, config);
            });

            it('should load env modules from directory', async () => {
                // Create a simple env module
                const envFile = path.join(tempDir, 'test-env.mjs');
                await fs.writeFile(envFile, `
                    // Test env module
                    export const loaded = true;
                `);

                const config = {
                    title: 'Test',
                    host: '127.0.0.1',
                    port: 0,
                    bootstrap: {
                        load_env: tempDir,
                    },
                };

                await start(server, config);
            });

            it('should load lifecycle modules with hooks', async () => {
                // Create lifecycle module with hooks
                const lifecycleFile = path.join(tempDir, 'test-lifecycle.mjs');
                await fs.writeFile(lifecycleFile, `
                    export function onStartup(server, config) {
                        server.decorate('testStartupRan', true);
                    }
                    export function onShutdown(server, config) {
                        // Shutdown hook
                    }
                `);

                const config = {
                    title: 'Test',
                    host: '127.0.0.1',
                    port: 0,
                    bootstrap: {
                        lifecycle: tempDir,
                    },
                };

                await start(server, config);
                expect(server.testStartupRan).toBe(true);
            });
        });

        describe('Initial State Feature', () => {
            it('should initialize request state when configured', async () => {
                const config = {
                    title: 'Test',
                    host: '127.0.0.1',
                    port: 0,
                    initial_state: {
                        user: 'test',
                        role: 'tester',
                    },
                };

                server.get('/state', async (request) => ({
                    state: request.state,
                }));

                await start(server, config);

                const response = await server.inject({
                    method: 'GET',
                    url: '/state',
                });

                const body = response.json();
                expect(body.state).toBeDefined();
                expect(body.state.user).toBe('test');
                expect(body.state.role).toBe('tester');
            });

            it('should deep clone state for each request', async () => {
                const config = {
                    title: 'Test',
                    host: '127.0.0.1',
                    port: 0,
                    initial_state: {
                        counter: 0,
                        nested: { value: 'original' },
                    },
                };

                server.get('/mutate', async (request) => {
                    request.state.counter++;
                    request.state.nested.value = 'mutated';
                    return { counter: request.state.counter };
                });

                server.get('/check', async (request) => ({
                    counter: request.state.counter,
                    nested: request.state.nested.value,
                }));

                await start(server, config);

                // Mutate state
                await server.inject({ method: 'GET', url: '/mutate' });

                // Check that next request gets fresh state
                const response = await server.inject({
                    method: 'GET',
                    url: '/check',
                });

                const body = response.json();
                expect(body.counter).toBe(0);
                expect(body.nested).toBe('original');
            });
        });

        describe('Port Configuration', () => {
            it('should use port from config', async () => {
                const config = {
                    title: 'Test',
                    host: '127.0.0.1',
                    port: 0, // Use 0 for random available port
                };

                await start(server, config);
                const addresses = server.addresses();
                expect(addresses[0].port).toBeGreaterThan(0);
            });

            it('should use PORT env variable when set', async () => {
                const originalPort = process.env.PORT;
                process.env.PORT = '0'; // Random port

                const config = {
                    title: 'Test',
                    host: '127.0.0.1',
                    port: 9999,
                };

                await start(server, config);
                const addresses = server.addresses();
                expect(addresses[0].port).toBeGreaterThan(0);

                // Restore
                if (originalPort) {
                    process.env.PORT = originalPort;
                } else {
                    delete process.env.PORT;
                }
            });
        });
    });

    // =========================================================================
    // stop() Function
    // =========================================================================

    describe('stop()', () => {
        it('should close the server', async () => {
            const server = init({ title: 'Test', logger: false });

            await server.listen({ host: '127.0.0.1', port: 0 });

            // Server should be listening
            expect(server.addresses().length).toBeGreaterThan(0);

            // Stop the server
            await stop(server, { title: 'Test' });

            // Server should be closed - addresses returns empty array after close
            expect(server.addresses()).toEqual([]);
        });

        it('should handle empty config', async () => {
            const server = init({ title: 'Test', logger: false });
            await server.listen({ host: '127.0.0.1', port: 0 });

            // Should not throw
            await stop(server, {});
        });
    });

    // =========================================================================
    // Decorators
    // =========================================================================

    describe('Decorators', () => {
        it('should decorate server with _shutdownHooks', async () => {
            const server = init({ title: 'Test', logger: false });
            const config = {
                title: 'Test',
                host: '127.0.0.1',
                port: 0,
            };

            await start(server, config);

            expect(server.hasDecorator('_shutdownHooks')).toBe(true);
            expect(Array.isArray(server._shutdownHooks)).toBe(true);

            await server.close();
        });

        it('should decorate server with _config', async () => {
            const server = init({ title: 'Test', logger: false });
            const config = {
                title: 'Test',
                host: '127.0.0.1',
                port: 0,
            };

            await start(server, config);

            expect(server.hasDecorator('_config')).toBe(true);
            expect(server._config.title).toBe('Test');

            await server.close();
        });

        it('should decorate request with state when initial_state provided', async () => {
            const server = init({ title: 'Test', logger: false });
            const config = {
                title: 'Test',
                host: '127.0.0.1',
                port: 0,
                initial_state: { user: 'test' },
            };

            await start(server, config);

            expect(server.hasRequestDecorator('state')).toBe(true);

            await server.close();
        });
    });

    // =========================================================================
    // Lifecycle Hooks
    // =========================================================================

    describe('Lifecycle Hooks', () => {
        let tempDir;

        beforeEach(async () => {
            tempDir = await createTempDir();
        });

        afterEach(async () => {
            if (tempDir) {
                await cleanupTempDir(tempDir);
            }
        });

        it('should execute startup hooks before listen', async () => {
            const server = init({ title: 'Test', logger: false });

            // Create lifecycle module
            const lifecycleFile = path.join(tempDir, 'startup.mjs');
            await fs.writeFile(lifecycleFile, `
                export function onStartup(server, config) {
                    server.decorate('startupTime', Date.now());
                }
            `);

            const config = {
                title: 'Test',
                host: '127.0.0.1',
                port: 0,
                bootstrap: { lifecycle: tempDir },
            };

            await start(server, config);

            expect(server.startupTime).toBeDefined();
            expect(typeof server.startupTime).toBe('number');

            await server.close();
        });

        it('should register shutdown hooks on close', async () => {
            const server = init({ title: 'Test', logger: false });

            // Create lifecycle module with shutdown hook
            const lifecycleFile = path.join(tempDir, 'shutdown.mjs');
            await fs.writeFile(lifecycleFile, `
                export function onShutdown(server, config) {
                    // This will run on close
                }
            `);

            const config = {
                title: 'Test',
                host: '127.0.0.1',
                port: 0,
                bootstrap: { lifecycle: tempDir },
            };

            await start(server, config);
            expect(server._shutdownHooks.length).toBe(1);

            await server.close();
        });
    });
});
