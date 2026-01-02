/**
 * Unit tests for ComputeRegistry module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 * - Log verification (hyper-observability)
 *
 * Following FORMAT_TEST.yaml specification.
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { ComputeRegistry } from '../src/compute-registry.js';
import { ComputeScope } from '../src/options.js';
import { ComputeFunctionError, ErrorCode } from '../src/errors.js';
import { MockLogger, createMockLogger } from './helpers/mock-logger.js';

describe('ComputeRegistry', () => {
    let registry: ComputeRegistry;
    let mockLogger: MockLogger;

    beforeEach(() => {
        mockLogger = createMockLogger();
        registry = new ComputeRegistry(mockLogger);
    });

    // =========================================================================
    // Statement Coverage
    // =========================================================================

    describe('StatementCoverage', () => {
        it('should register and resolve basic function', async () => {
            registry.register('test_fn', () => 'result', ComputeScope.REQUEST);

            expect(registry.has('test_fn')).toBe(true);
            expect(registry.list()).toContain('test_fn');
        });

        it('should resolve sync function with context', async () => {
            registry.register('sync_fn', (ctx: any) => `hello-${ctx?.name || 'world'}`, ComputeScope.REQUEST);

            const result = await registry.resolve('sync_fn', { name: 'test' });

            expect(result).toBe('hello-test');
        });

        it('should resolve async function', async () => {
            const asyncFn = async (ctx: any) => `async-${ctx?.value || 0}`;
            registry.register('async_fn', asyncFn, ComputeScope.REQUEST);

            const result = await registry.resolve('async_fn', { value: 42 });

            expect(result).toBe('async-42');
        });

        it('should unregister function', () => {
            registry.register('temp_fn', () => 'temp', ComputeScope.REQUEST);
            expect(registry.has('temp_fn')).toBe(true);

            registry.unregister('temp_fn');

            expect(registry.has('temp_fn')).toBe(false);
        });

        it('should clear all functions', () => {
            registry.register('fn1', () => 1, ComputeScope.REQUEST);
            registry.register('fn2', () => 2, ComputeScope.STARTUP);

            registry.clear();

            expect(registry.list()).toEqual([]);
        });

        it('should return correct scope for function', () => {
            registry.register('startup_fn', () => 's', ComputeScope.STARTUP);
            registry.register('request_fn', () => 'r', ComputeScope.REQUEST);

            expect(registry.getScope('startup_fn')).toBe(ComputeScope.STARTUP);
            expect(registry.getScope('request_fn')).toBe(ComputeScope.REQUEST);
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('BranchCoverage', () => {
        it('should cache STARTUP function results', async () => {
            let callCount = 0;
            registry.register('cached_fn', () => {
                callCount++;
                return `call-${callCount}`;
            }, ComputeScope.STARTUP);

            const result1 = await registry.resolve('cached_fn');
            const result2 = await registry.resolve('cached_fn');

            expect(result1).toBe('call-1');
            expect(result2).toBe('call-1'); // Same cached result
            expect(callCount).toBe(1); // Only called once
        });

        it('should not cache REQUEST function results', async () => {
            let callCount = 0;
            registry.register('uncached_fn', () => {
                callCount++;
                return `call-${callCount}`;
            }, ComputeScope.REQUEST);

            const result1 = await registry.resolve('uncached_fn');
            const result2 = await registry.resolve('uncached_fn');

            expect(result1).toBe('call-1');
            expect(result2).toBe('call-2');
            expect(callCount).toBe(2);
        });

        it('should return undefined scope for unknown function', () => {
            const result = registry.getScope('unknown_fn');

            expect(result).toBeUndefined();
        });

        it('should handle unregister of unknown function as noop', () => {
            // Should not throw
            registry.unregister('nonexistent');

            expect(registry.has('nonexistent')).toBe(false);
        });

        it('should work with functions that do not accept context', async () => {
            registry.register('no_ctx_fn', () => 'no-context', ComputeScope.REQUEST);

            const result = await registry.resolve('no_ctx_fn', { some: 'context' });

            expect(result).toBe('no-context');
        });
    });

    // =========================================================================
    // Boundary Value Analysis
    // =========================================================================

    describe('BoundaryValueAnalysis', () => {
        it('should throw for empty function name', () => {
            expect(() => {
                registry.register('', () => 'x', ComputeScope.REQUEST);
            }).toThrow('cannot be empty');
        });

        it('should throw for invalid function name starting with number', () => {
            expect(() => {
                registry.register('123invalid', () => 'x', ComputeScope.REQUEST);
            }).toThrow(/Invalid function name/);
        });

        it('should throw for function name with dash', () => {
            expect(() => {
                registry.register('fn-with-dash', () => 'x', ComputeScope.REQUEST);
            }).toThrow(/Invalid function name/);
        });

        it('should throw for function name with dot', () => {
            expect(() => {
                registry.register('fn.with.dot', () => 'x', ComputeScope.REQUEST);
            }).toThrow(/Invalid function name/);
        });

        it('should accept valid function names', () => {
            registry.register('valid_fn', () => 'a', ComputeScope.REQUEST);
            registry.register('_private_fn', () => 'b', ComputeScope.REQUEST);
            registry.register('CamelCase', () => 'c', ComputeScope.REQUEST);
            registry.register('fn123', () => 'd', ComputeScope.REQUEST);

            expect(registry.has('valid_fn')).toBe(true);
            expect(registry.has('_private_fn')).toBe(true);
            expect(registry.has('CamelCase')).toBe(true);
            expect(registry.has('fn123')).toBe(true);
        });

        it('should overwrite on duplicate registration', () => {
            registry.register('dup_fn', () => 'first', ComputeScope.REQUEST);
            registry.register('dup_fn', () => 'second', ComputeScope.REQUEST);

            expect(registry.list().filter(n => n === 'dup_fn').length).toBe(1);
        });
    });

    // =========================================================================
    // Error Handling
    // =========================================================================

    describe('ErrorHandling', () => {
        it('should throw ComputeFunctionError for unknown function', async () => {
            await expect(registry.resolve('unknown_fn')).rejects.toThrow(ComputeFunctionError);

            try {
                await registry.resolve('unknown_fn');
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.COMPUTE_FUNCTION_NOT_FOUND);
                expect(e.message).toContain('unknown_fn');
            }
        });

        it('should wrap function exceptions in ComputeFunctionError', async () => {
            registry.register('failing_fn', () => {
                throw new Error('Internal failure');
            }, ComputeScope.REQUEST);

            await expect(registry.resolve('failing_fn')).rejects.toThrow(ComputeFunctionError);

            try {
                await registry.resolve('failing_fn');
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.COMPUTE_FUNCTION_FAILED);
                expect(e.message).toContain('failing_fn');
            }
        });

        it('should wrap async function exceptions correctly', async () => {
            registry.register('async_fail', async () => {
                throw new Error('Async failure');
            }, ComputeScope.REQUEST);

            await expect(registry.resolve('async_fail')).rejects.toThrow(ComputeFunctionError);

            try {
                await registry.resolve('async_fail');
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.COMPUTE_FUNCTION_FAILED);
            }
        });
    });

    // =========================================================================
    // Log Verification
    // =========================================================================

    describe('LogVerification', () => {
        it('should log debug and info on register', () => {
            registry.register('logged_fn', () => 'x', ComputeScope.REQUEST);

            expect(mockLogger.contains('debug', 'Registering function: logged_fn')).toBe(true);
            expect(mockLogger.contains('info', 'Function registered: logged_fn')).toBe(true);
        });

        it('should log when function found on unregister', () => {
            registry.register('to_remove', () => 'x', ComputeScope.REQUEST);
            registry.unregister('to_remove');

            expect(mockLogger.contains('debug', 'Unregistering function: to_remove')).toBe(true);
            expect(mockLogger.contains('info', 'Function unregistered: to_remove')).toBe(true);
        });

        it('should log debug on resolve', async () => {
            registry.register('resolve_test', () => 'x', ComputeScope.REQUEST);
            await registry.resolve('resolve_test');

            expect(mockLogger.contains('debug', 'Resolving function: resolve_test')).toBe(true);
        });

        it('should log cache hit for STARTUP functions', async () => {
            registry.register('cached', () => 'x', ComputeScope.STARTUP);
            await registry.resolve('cached'); // First call
            await registry.resolve('cached'); // Second call - cache hit

            expect(mockLogger.contains('debug', 'Returning cached value for: cached')).toBe(true);
        });

        it('should log error on failed resolve', async () => {
            registry.register('error_fn', () => { throw new Error('fail'); }, ComputeScope.REQUEST);

            try {
                await registry.resolve('error_fn');
            } catch (e) {
                // Expected
            }

            expect(mockLogger.contains('error', 'Function execution failed: error_fn')).toBe(true);
        });

        it('should log debug on clear', () => {
            registry.clear();

            expect(mockLogger.contains('debug', 'Clearing registry')).toBe(true);
        });

        it('should log debug on clearCache', () => {
            registry.clearCache();

            expect(mockLogger.contains('debug', 'Clearing result cache')).toBe(true);
        });
    });

    // =========================================================================
    // Integration Tests
    // =========================================================================

    describe('Integration', () => {
        it('should handle realistic compute function flow', async () => {
            // Register mix of STARTUP and REQUEST functions
            registry.register('get_build_id', () => 'build-123', ComputeScope.STARTUP);
            registry.register(
                'get_user_id',
                (ctx: any) => ctx?.user?.id || 'anon',
                ComputeScope.REQUEST
            );

            // Resolve STARTUP (should cache)
            const build1 = await registry.resolve('get_build_id');
            const build2 = await registry.resolve('get_build_id');
            expect(build1).toBe('build-123');
            expect(build2).toBe('build-123');

            // Resolve REQUEST with context
            const userId = await registry.resolve('get_user_id', { user: { id: 'usr-456' } });
            expect(userId).toBe('usr-456');

            // Clear cache
            registry.clearCache();

            // Full clear
            registry.clear();
            expect(registry.list()).toEqual([]);
        });
    });
});
