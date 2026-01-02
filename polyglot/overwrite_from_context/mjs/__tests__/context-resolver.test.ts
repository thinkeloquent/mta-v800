/**
 * Unit tests for ContextResolver module.
 *
 * Tests cover:
 * - Template pattern resolution
 * - Compute pattern resolution
 * - Object resolution (recursive)
 * - Scope enforcement
 * - Default value handling
 *
 * Following FORMAT_TEST.yaml specification.
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { ContextResolver } from '../src/context-resolver.js';
import { ComputeRegistry } from '../src/compute-registry.js';
import { ComputeScope, MissingStrategy } from '../src/options.js';
import {
    ComputeFunctionError,
    RecursionLimitError,
    ScopeViolationError,
    SecurityError,
    ErrorCode
} from '../src/errors.js';
import { MockLogger, createMockLogger } from './helpers/mock-logger.js';

describe('ContextResolver', () => {
    let registry: ComputeRegistry;
    let resolver: ContextResolver;
    let mockLogger: MockLogger;

    beforeEach(() => {
        mockLogger = createMockLogger();
        registry = new ComputeRegistry(mockLogger);
        resolver = new ContextResolver(registry, { logger: mockLogger });
    });

    // =========================================================================
    // Statement Coverage
    // =========================================================================

    describe('StatementCoverage', () => {
        it('should correctly identify compute pattern', () => {
            expect(resolver.isComputePattern('{{fn:my_function}}')).toBe(true);
            expect(resolver.isComputePattern('{{fn:get_value | \'default\'}}')).toBe(true);
        });

        it('should correctly reject non-compute patterns', () => {
            expect(resolver.isComputePattern('{{variable}}')).toBe(false);
            expect(resolver.isComputePattern('plain text')).toBe(false);
            expect(resolver.isComputePattern('{{env.HOST}}')).toBe(false);
        });

        it('should resolve template pattern from context', async () => {
            const context = { env: { HOST: 'localhost' } };

            const result = await resolver.resolve('{{env.HOST}}', context);

            expect(result).toBe('localhost');
        });

        it('should return literal strings as-is', async () => {
            const result = await resolver.resolve('plain text', {});

            expect(result).toBe('plain text');
        });

        it('should pass through non-string values unchanged', async () => {
            expect(await resolver.resolve(42, {})).toBe(42);
            expect(await resolver.resolve(true, {})).toBe(true);
            expect(await resolver.resolve(null, {})).toBeNull();
            expect(await resolver.resolve([1, 2, 3], {})).toEqual([1, 2, 3]);
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('BranchCoverage', () => {
        it('should use default when template value is missing', async () => {
            const result = await resolver.resolve('{{missing.value | \'default_val\'}}', {});

            expect(result).toBe('default_val');
        });

        it('should return original when missing and IGNORE strategy', async () => {
            const resolver = new ContextResolver(registry, {
                logger: mockLogger,
                missingStrategy: MissingStrategy.IGNORE
            });

            const result = await resolver.resolve('{{missing.value}}', {});

            expect(result).toBe('{{missing.value}}');
        });

        it('should resolve compute pattern to registered function', async () => {
            registry.register('get_value', () => 'computed', ComputeScope.REQUEST);

            const result = await resolver.resolve('{{fn:get_value}}', {});

            expect(result).toBe('computed');
        });

        it('should use default when compute function missing', async () => {
            const result = await resolver.resolve('{{fn:missing_fn | \'fallback\'}}', {});

            expect(result).toBe('fallback');
        });

        it('should use default when compute function fails', async () => {
            registry.register('failing_fn', () => { throw new Error('fail'); }, ComputeScope.REQUEST);

            const result = await resolver.resolve('{{fn:failing_fn | \'error_fallback\'}}', {});

            expect(result).toBe('error_fallback');
        });
    });

    // =========================================================================
    // Object Resolution
    // =========================================================================

    describe('ObjectResolution', () => {
        it('should resolve dictionary values', async () => {
            const context = { env: { HOST: 'db.example.com', PORT: '5432' } };
            const obj = {
                host: '{{env.HOST}}',
                port: '{{env.PORT}}',
                name: 'static_value'
            };

            const result = await resolver.resolveObject(obj, context);

            expect(result.host).toBe('db.example.com');
            expect(result.port).toBe('5432');
            expect(result.name).toBe('static_value');
        });

        it('should resolve deeply nested dictionaries', async () => {
            const context = { config: { db: { host: 'localhost' } } };
            const obj = {
                level1: {
                    level2: {
                        value: '{{config.db.host}}'
                    }
                }
            };

            const result = await resolver.resolveObject(obj, context);

            expect(result.level1.level2.value).toBe('localhost');
        });

        it('should resolve list elements', async () => {
            const context = { items: { a: 'A', b: 'B' } };
            const obj = ['{{items.a}}', '{{items.b}}', 'static'];

            const result = await resolver.resolveObject(obj, context);

            expect(result).toEqual(['A', 'B', 'static']);
        });

        it('should resolve mixed dict/list structures with compute', async () => {
            registry.register('get_id', () => 'id-123', ComputeScope.REQUEST);

            const context = { env: { MODE: 'production' } };
            const obj = {
                mode: '{{env.MODE}}',
                id: '{{fn:get_id}}',
                items: [
                    { name: 'item1' },
                    { value: '{{env.MODE}}' }
                ]
            };

            const result = await resolver.resolveObject(obj, context);

            expect(result.mode).toBe('production');
            expect(result.id).toBe('id-123');
            expect(result.items[1].value).toBe('production');
        });

        it('should preserve non-string values unchanged', async () => {
            const obj = {
                number: 42,
                boolean: true,
                null: null,
                list: [1, 2, 3]
            };

            const result = await resolver.resolveObject(obj, {});

            expect(result.number).toBe(42);
            expect(result.boolean).toBe(true);
            expect(result.null).toBeNull();
            expect(result.list).toEqual([1, 2, 3]);
        });
    });

    // =========================================================================
    // Scope Enforcement
    // =========================================================================

    describe('ScopeEnforcement', () => {
        it('should allow STARTUP function at STARTUP scope', async () => {
            registry.register('startup_fn', () => 'startup', ComputeScope.STARTUP);

            const result = await resolver.resolve(
                '{{fn:startup_fn}}',
                {},
                ComputeScope.STARTUP
            );

            expect(result).toBe('startup');
        });

        it('should block REQUEST function at STARTUP scope', async () => {
            registry.register('request_fn', () => 'request', ComputeScope.REQUEST);

            await expect(resolver.resolve(
                '{{fn:request_fn}}',
                {},
                ComputeScope.STARTUP
            )).rejects.toThrow(ScopeViolationError);

            try {
                await resolver.resolve('{{fn:request_fn}}', {}, ComputeScope.STARTUP);
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.SCOPE_VIOLATION);
            }
        });

        it('should allow both scopes at REQUEST scope', async () => {
            registry.register('startup_fn', () => 's', ComputeScope.STARTUP);
            registry.register('request_fn', () => 'r', ComputeScope.REQUEST);

            const sResult = await resolver.resolve(
                '{{fn:startup_fn}}',
                {},
                ComputeScope.REQUEST
            );
            const rResult = await resolver.resolve(
                '{{fn:request_fn}}',
                {},
                ComputeScope.REQUEST
            );

            expect(sResult).toBe('s');
            expect(rResult).toBe('r');
        });
    });

    // =========================================================================
    // Recursion Protection
    // =========================================================================

    describe('RecursionProtection', () => {
        it('should throw when max depth exceeded', async () => {
            const resolver = new ContextResolver(registry, {
                logger: mockLogger,
                maxDepth: 5
            });

            await expect(resolver.resolve('{{test}}', {}, ComputeScope.REQUEST, 10)).rejects.toThrow(RecursionLimitError);

            try {
                await resolver.resolve('{{test}}', {}, ComputeScope.REQUEST, 10);
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.RECURSION_LIMIT);
            }
        });

        it('should succeed for deeply nested object within limit', async () => {
            const resolver = new ContextResolver(registry, {
                logger: mockLogger,
                maxDepth: 20
            });

            const obj = { l1: { l2: { l3: { l4: { value: '{{env.X | \'deep\'}}' } } } } };

            const result = await resolver.resolveObject(obj, {});

            expect(result.l1.l2.l3.l4.value).toBe('deep');
        });
    });

    // =========================================================================
    // Default Value Parsing
    // =========================================================================

    describe('DefaultValueParsing', () => {
        it('should parse \'true\' as boolean true', async () => {
            const result = await resolver.resolve('{{missing | \'true\'}}', {});
            expect(result).toBe(true);
        });

        it('should parse \'false\' as boolean false', async () => {
            const result = await resolver.resolve('{{missing | \'false\'}}', {});
            expect(result).toBe(false);
        });

        it('should parse numeric string as integer', async () => {
            const result = await resolver.resolve('{{missing | \'42\'}}', {});
            expect(result).toBe(42);
            expect(typeof result).toBe('number');
        });

        it('should parse float string as float', async () => {
            const result = await resolver.resolve('{{missing | \'3.14\'}}', {});
            expect(result).toBe(3.14);
            expect(typeof result).toBe('number');
        });

        it('should keep regular string as string', async () => {
            const result = await resolver.resolve('{{missing | \'hello\'}}', {});
            expect(result).toBe('hello');
            expect(typeof result).toBe('string');
        });
    });

    // =========================================================================
    // Security Integration
    // =========================================================================

    describe('SecurityIntegration', () => {
        it('should raise SecurityError for blocked paths', async () => {
            await expect(resolver.resolve('{{obj.__proto__}}', {})).rejects.toThrow(SecurityError);
        });

        it('should block underscore prefix paths', async () => {
            await expect(resolver.resolve('{{_private.value}}', {})).rejects.toThrow(SecurityError);
        });
    });

    // =========================================================================
    // Batch Resolution
    // =========================================================================

    describe('BatchResolution', () => {
        it('should resolve multiple expressions in order', async () => {
            registry.register('get_id', () => 'ID', ComputeScope.REQUEST);

            const context = { env: { A: 'a', B: 'b' } };
            const expressions = ['{{env.A}}', '{{env.B}}', '{{fn:get_id}}', 'literal'];

            const results = await resolver.resolveMany(expressions, context);

            expect(results).toEqual(['a', 'b', 'ID', 'literal']);
        });

        it('should return empty list for empty expressions', async () => {
            const results = await resolver.resolveMany([], {});

            expect(results).toEqual([]);
        });
    });

    // =========================================================================
    // Integration Tests
    // =========================================================================

    describe('Integration', () => {
        it('should handle realistic config resolution', async () => {
            // Register compute functions
            registry.register(
                'get_connection_string',
                (ctx: any) => `postgresql://${ctx?.env?.DB_HOST || 'localhost'}:5432/app`,
                ComputeScope.STARTUP
            );
            registry.register(
                'get_request_id',
                (ctx: any) => ctx?.request?.id || 'unknown',
                ComputeScope.REQUEST
            );

            const config = {
                database: {
                    connection: '{{fn:get_connection_string}}',
                    pool_size: 10
                },
                app: {
                    name: '{{env.APP_NAME | \'MyApp\'}}',
                    debug: '{{env.DEBUG | \'false\'}}'
                },
                request: {
                    id: '{{fn:get_request_id}}'
                }
            };

            const context = {
                env: { DB_HOST: 'db.prod.example.com', APP_NAME: 'ProductionApp' },
                request: { id: 'req-12345' }
            };

            const result = await resolver.resolveObject(config, context, ComputeScope.REQUEST);

            expect(result.database.connection).toBe('postgresql://db.prod.example.com:5432/app');
            expect(result.database.pool_size).toBe(10);
            expect(result.app.name).toBe('ProductionApp');
            expect(result.app.debug).toBe(false);
            expect(result.request.id).toBe('req-12345');
        });
    });
});
