/**
 * Integration tests for Fastify integration module.
 *
 * Tests cover:
 * - contextResolverPlugin setup
 * - STARTUP resolution
 * - REQUEST resolution via onRequest hook
 * - Instance and request property decoration
 * - Full request/response cycle
 *
 * Following FORMAT_TEST.yaml specification.
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Fastify, { FastifyInstance } from 'fastify';
import { ComputeScope } from '../src/options.js';
import { ComputeRegistry } from '../src/compute-registry.js';
import { contextResolverPlugin } from '../src/integrations/fastify.js';
import { MockLogger, createMockLogger } from './helpers/mock-logger.js';

describe('FastifyIntegration', () => {
    let app: FastifyInstance;
    let registry: ComputeRegistry;
    let mockLogger: MockLogger;

    beforeEach(() => {
        mockLogger = createMockLogger();
        registry = new ComputeRegistry(mockLogger);
        app = Fastify({ logger: false });
    });

    afterEach(async () => {
        await app.close();
    });

    // =========================================================================
    // Statement Coverage
    // =========================================================================

    describe('StatementCoverage', () => {
        it('should register plugin with config', async () => {
            const config = { app: { name: 'test' } };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                logger: mockLogger
            });

            await app.ready();

            expect((app as any).config).toBeDefined();
            expect((app as any).config.app.name).toBe('test');
        });

        it('should resolve template patterns at startup', async () => {
            const config = {
                app: {
                    name: '{{env.APP_NAME | \'DefaultApp\'}}',
                    version: '1.0.0'
                }
            };

            // Set env
            const originalEnv = process.env.APP_NAME;
            process.env.APP_NAME = 'TestApp';

            try {
                await app.register(contextResolverPlugin, {
                    config,
                    registry,
                    logger: mockLogger
                });

                await app.ready();

                expect((app as any).config.app.name).toBe('TestApp');
                expect((app as any).config.app.version).toBe('1.0.0');
            } finally {
                if (originalEnv === undefined) {
                    delete process.env.APP_NAME;
                } else {
                    process.env.APP_NAME = originalEnv;
                }
            }
        });

        it('should resolve compute patterns at startup', async () => {
            registry.register('get_version', () => '2.0.0', ComputeScope.STARTUP);

            const config = {
                version: '{{fn:get_version}}'
            };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                logger: mockLogger
            });

            await app.ready();

            expect((app as any).config.version).toBe('2.0.0');
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('BranchCoverage', () => {
        it('should handle custom instanceProperty', async () => {
            const config = { key: 'value' };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                instanceProperty: 'resolvedConfig',
                logger: mockLogger
            });

            await app.ready();

            expect((app as any).resolvedConfig).toBeDefined();
            expect((app as any).resolvedConfig.key).toBe('value');
        });

        it('should handle dotted instanceProperty', async () => {
            const config = { key: 'value' };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                instanceProperty: 'state.config',
                logger: mockLogger
            });

            await app.ready();

            expect((app as any).state).toBeDefined();
            expect((app as any).state.config.key).toBe('value');
        });

        it('should use defaults when env vars missing', async () => {
            const config = {
                database: {
                    host: '{{env.MISSING_DB_HOST | \'localhost\'}}',
                    port: '{{env.MISSING_DB_PORT | \'5432\'}}'
                }
            };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                logger: mockLogger
            });

            await app.ready();

            expect((app as any).config.database.host).toBe('localhost');
            expect((app as any).config.database.port).toBe(5432);
        });
    });

    // =========================================================================
    // Request Resolution
    // =========================================================================

    describe('RequestResolution', () => {
        it('should decorate request with resolved config', async () => {
            // Clear any existing MODE env var to ensure default is used
            const originalMode = process.env.MODE;
            delete process.env.MODE;

            try {
                const config = {
                    mode: '{{env.MODE | \'development\'}}'
                };

                await app.register(contextResolverPlugin, {
                    config,
                    registry,
                    logger: mockLogger
                });

                app.get('/config', async (request) => {
                    return { config: (request as any).config };
                });

                await app.ready();

                const response = await app.inject({
                    method: 'GET',
                    url: '/config'
                });

                expect(response.statusCode).toBe(200);
                const body = JSON.parse(response.body);
                expect(body.config.mode).toBe('development');
            } finally {
                if (originalMode !== undefined) {
                    process.env.MODE = originalMode;
                }
            }
        });

        it('should handle custom requestProperty', async () => {
            const config = { key: 'value' };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                requestProperty: 'resolvedConfig',
                logger: mockLogger
            });

            app.get('/config', async (request) => {
                return { config: (request as any).resolvedConfig };
            });

            await app.ready();

            const response = await app.inject({
                method: 'GET',
                url: '/config'
            });

            expect(response.statusCode).toBe(200);
            const body = JSON.parse(response.body);
            expect(body.config.key).toBe('value');
        });

        it('should provide resolveContext helper on request', async () => {
            registry.register('get_value', () => 'dynamic', ComputeScope.REQUEST);

            const config = {};

            await app.register(contextResolverPlugin, {
                config,
                registry,
                logger: mockLogger
            });

            app.get('/resolve', async (request) => {
                const value = await (request as any).resolveContext('{{fn:get_value}}');
                return { value };
            });

            await app.ready();

            const response = await app.inject({
                method: 'GET',
                url: '/resolve'
            });

            expect(response.statusCode).toBe(200);
            const body = JSON.parse(response.body);
            expect(body.value).toBe('dynamic');
        });
    });

    // =========================================================================
    // Scope Enforcement
    // =========================================================================

    describe('ScopeEnforcement', () => {
        it('should cache STARTUP function results', async () => {
            let callCount = 0;
            registry.register('counting_startup', () => {
                callCount++;
                return `call-${callCount}`;
            }, ComputeScope.STARTUP);

            const config = {
                counter: '{{fn:counting_startup}}'
            };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                logger: mockLogger
            });

            app.get('/config', async (request) => {
                return { config: (request as any).config };
            });

            await app.ready();

            // Make multiple requests
            const response1 = await app.inject({ method: 'GET', url: '/config' });
            const response2 = await app.inject({ method: 'GET', url: '/config' });
            const response3 = await app.inject({ method: 'GET', url: '/config' });

            const body1 = JSON.parse(response1.body);
            const body2 = JSON.parse(response2.body);
            const body3 = JSON.parse(response3.body);

            // All should return same cached value
            expect(body1.config.counter).toBe('call-1');
            expect(body2.config.counter).toBe('call-1');
            expect(body3.config.counter).toBe('call-1');
        });

        it('should call REQUEST function on each request via resolveContext', async () => {
            let callCount = 0;
            registry.register('counting_request', () => {
                callCount++;
                return `req-${callCount}`;
            }, ComputeScope.REQUEST);

            // Config without REQUEST-scope patterns (those would fail at STARTUP)
            const config = {
                static: 'value'
            };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                logger: mockLogger
            });

            // Use resolveContext helper to call REQUEST functions
            app.get('/counter', async (request) => {
                const counter = await (request as any).resolveContext('{{fn:counting_request}}');
                return { counter };
            });

            await app.ready();

            const response1 = await app.inject({ method: 'GET', url: '/counter' });
            const response2 = await app.inject({ method: 'GET', url: '/counter' });

            const body1 = JSON.parse(response1.body);
            const body2 = JSON.parse(response2.body);

            expect(body1.counter).toBe('req-1');
            expect(body2.counter).toBe('req-2');
        });
    });

    // =========================================================================
    // Integration Tests
    // =========================================================================

    describe('Integration', () => {
        it('should handle realistic database config scenario', async () => {
            // Register connection string builder (STARTUP scope - cached)
            registry.register(
                'build_connection_string',
                (ctx: any) => {
                    const host = ctx?.env?.DB_HOST || 'localhost';
                    const port = ctx?.env?.DB_PORT || '5432';
                    const name = ctx?.env?.DB_NAME || 'app';
                    return `postgresql://${host}:${port}/${name}`;
                },
                ComputeScope.STARTUP
            );

            // Register request ID generator (REQUEST scope)
            let reqCount = 0;
            registry.register(
                'get_request_id',
                () => {
                    reqCount++;
                    return `req-${reqCount}`;
                },
                ComputeScope.REQUEST
            );

            // Config with only STARTUP-safe patterns
            // REQUEST scope functions are resolved via resolveContext
            const config = {
                database: {
                    connection: '{{fn:build_connection_string}}',
                    pool_size: 10,
                    timeout: '{{env.DB_TIMEOUT | \'30\'}}'
                }
            };

            // Set env
            const originalHost = process.env.DB_HOST;
            process.env.DB_HOST = 'db.production.example.com';

            try {
                await app.register(contextResolverPlugin, {
                    config,
                    registry,
                    logger: mockLogger
                });

                app.get('/config', async (request) => {
                    // Get static config and add request-specific data
                    const baseConfig = (request as any).config;
                    const requestId = await (request as any).resolveContext('{{fn:get_request_id}}');
                    return {
                        ...baseConfig,
                        request: { id: requestId }
                    };
                });

                await app.ready();

                // Instance config has STARTUP resolved
                expect((app as any).config.database.connection)
                    .toBe('postgresql://db.production.example.com:5432/app');
                expect((app as any).config.database.pool_size).toBe(10);
                expect((app as any).config.database.timeout).toBe(30);

                // Make requests
                const response1 = await app.inject({ method: 'GET', url: '/config' });
                const response2 = await app.inject({ method: 'GET', url: '/config' });

                const body1 = JSON.parse(response1.body);
                const body2 = JSON.parse(response2.body);

                expect(body1.request.id).toBe('req-1');
                expect(body2.request.id).toBe('req-2');

                // Connection string should be same (STARTUP cached)
                expect(body1.database.connection)
                    .toBe('postgresql://db.production.example.com:5432/app');
                expect(body2.database.connection)
                    .toBe('postgresql://db.production.example.com:5432/app');
            } finally {
                if (originalHost === undefined) {
                    delete process.env.DB_HOST;
                } else {
                    process.env.DB_HOST = originalHost;
                }
            }
        });

        it('should handle multiple routes with shared config', async () => {
            const config = {
                version: '{{env.APP_VERSION | \'1.0.0\'}}',
                debug: '{{env.DEBUG | \'false\'}}'
            };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                logger: mockLogger
            });

            app.get('/health', async (request) => {
                return { status: 'ok', version: (request as any).config.version };
            });

            app.get('/settings', async (request) => {
                return { debug: (request as any).config.debug };
            });

            await app.ready();

            const healthResponse = await app.inject({ method: 'GET', url: '/health' });
            const settingsResponse = await app.inject({ method: 'GET', url: '/settings' });

            const healthBody = JSON.parse(healthResponse.body);
            const settingsBody = JSON.parse(settingsResponse.body);

            expect(healthBody.version).toBe('1.0.0');
            expect(settingsBody.debug).toBe(false);
        });
    });

    // =========================================================================
    // Error Handling
    // =========================================================================

    describe('ErrorHandling', () => {
        it('should handle compute function errors gracefully with default', async () => {
            registry.register('failing_fn', () => {
                throw new Error('Intentional failure');
            }, ComputeScope.STARTUP);

            const config = {
                value: '{{fn:failing_fn | \'fallback\'}}'
            };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                logger: mockLogger
            });

            await app.ready();

            expect((app as any).config.value).toBe('fallback');
        });
    });

    // =========================================================================
    // Log Verification
    // =========================================================================

    describe('LogVerification', () => {
        it('should log plugin registration', async () => {
            const config = { key: 'value' };

            await app.register(contextResolverPlugin, {
                config,
                registry,
                logger: mockLogger
            });

            await app.ready();

            expect(mockLogger.contains('debug', 'Resolving configuration')).toBe(true);
            expect(mockLogger.contains('debug', 'Context Resolver plugin registered')).toBe(true);
        });
    });
});
