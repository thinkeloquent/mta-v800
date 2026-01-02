/**
 * Unit tests for context-builder module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { ContextBuilder } from '../src/context-builder.ts';
import { createMockRequest } from './helpers/test-utils.mjs';

describe('ContextBuilder', () => {
    // Store original env
    let originalEnv;

    beforeEach(() => {
        originalEnv = { ...process.env };
    });

    afterEach(() => {
        process.env = originalEnv;
    });

    // =========================================================================
    // Statement Coverage
    // =========================================================================

    describe('Statement Coverage', () => {
        it('should return a context object', async () => {
            const options = { config: { key: 'value' } };

            const result = await ContextBuilder.build(options);

            expect(typeof result).toBe('object');
        });

        it('should include env in context', async () => {
            const result = await ContextBuilder.build({});

            expect(result).toHaveProperty('env');
            expect(typeof result.env).toBe('object');
        });

        it('should include config in context', async () => {
            const options = { config: { app: { name: 'Test' } } };

            const result = await ContextBuilder.build(options);

            expect(result.config).toEqual({ app: { name: 'Test' } });
        });

        it('should include app in context', async () => {
            const options = { app: { name: 'MyApp', version: '1.0' } };

            const result = await ContextBuilder.build(options);

            expect(result.app).toEqual({ name: 'MyApp', version: '1.0' });
        });

        it('should include state in context', async () => {
            const options = { state: { userId: 123 } };

            const result = await ContextBuilder.build(options);

            expect(result.state).toEqual({ userId: 123 });
        });

        it('should include request in context', async () => {
            const mockRequest = createMockRequest();
            const options = { request: mockRequest };

            const result = await ContextBuilder.build(options);

            expect(result.request).toBe(mockRequest);
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('Branch Coverage', () => {
        it('should work without extenders', async () => {
            const options = { config: { key: 'value' } };

            const result = await ContextBuilder.build(options);

            expect(result.config).toEqual({ key: 'value' });
        });

        it('should work with empty extenders array', async () => {
            const options = { config: { key: 'value' } };

            const result = await ContextBuilder.build(options, []);

            expect(result.config).toEqual({ key: 'value' });
        });

        it('should apply single extender', async () => {
            const extender = async (ctx, req) => ({ custom: 'value' });
            const options = { config: { key: 'original' } };

            const result = await ContextBuilder.build(options, [extender]);

            expect(result.custom).toBe('value');
            expect(result.config).toEqual({ key: 'original' });
        });

        it('should apply multiple extenders in order', async () => {
            const extender1 = async (ctx, req) => ({ fromExt1: 'value1' });
            const extender2 = async (ctx, req) => ({ fromExt2: 'value2' });
            const options = {};

            const result = await ContextBuilder.build(options, [extender1, extender2]);

            expect(result.fromExt1).toBe('value1');
            expect(result.fromExt2).toBe('value2');
        });

        it('should allow extenders to see previous context', async () => {
            const extender1 = async (ctx, req) => ({ step1: true });
            const extender2 = async (ctx, req) => {
                if (ctx.step1) {
                    return { step2: 'sawStep1' };
                }
                return { step2: 'noStep1' };
            };

            const result = await ContextBuilder.build({}, [extender1, extender2]);

            expect(result.step2).toBe('sawStep1');
        });

        it('should use custom env if provided', async () => {
            const customEnv = { MY_VAR: 'my_value' };
            const options = { env: customEnv };

            const result = await ContextBuilder.build(options);

            expect(result.env).toBe(customEnv);
        });

        it('should default env to process.env', async () => {
            process.env.TEST_VAR = 'test_value';
            const options = {};

            const result = await ContextBuilder.build(options);

            expect(result.env.TEST_VAR).toBe('test_value');
        });
    });

    // =========================================================================
    // Boundary Values
    // =========================================================================

    describe('Boundary Values', () => {
        it('should handle empty options', async () => {
            const result = await ContextBuilder.build({});

            expect(result).toHaveProperty('env');
            expect(result).toHaveProperty('config');
            expect(result).toHaveProperty('app');
            expect(result).toHaveProperty('state');
            expect(result).toHaveProperty('request');
        });

        it('should handle empty config', async () => {
            const result = await ContextBuilder.build({ config: {} });

            expect(result.config).toEqual({});
        });

        it('should handle undefined request', async () => {
            const result = await ContextBuilder.build({ request: undefined });

            expect(result.request).toBeUndefined();
        });

        it('should handle null request', async () => {
            const result = await ContextBuilder.build({ request: null });

            expect(result.request).toBeNull();
        });

        it('should handle deeply nested config', async () => {
            const deepConfig = {
                level1: { level2: { level3: { level4: 'value' } } }
            };

            const result = await ContextBuilder.build({ config: deepConfig });

            expect(result.config.level1.level2.level3.level4).toBe('value');
        });
    });

    // =========================================================================
    // Error Handling
    // =========================================================================

    describe('Error Handling', () => {
        it('should propagate extender exceptions', async () => {
            const badExtender = async (ctx, req) => {
                throw new Error('Extender error');
            };

            await expect(
                ContextBuilder.build({}, [badExtender])
            ).rejects.toThrow('Extender error');
        });

        it('should handle sync extenders', async () => {
            const syncExtender = (ctx, req) => ({ sync: 'value' });

            const result = await ContextBuilder.build({}, [syncExtender]);

            expect(result.sync).toBe('value');
        });
    });

    // =========================================================================
    // Integration Tests
    // =========================================================================

    describe('Integration', () => {
        it('should build full context with all options and request', async () => {
            const mockRequest = createMockRequest({
                headers: { 'x-request-id': 'abc-123' }
            });

            const authExtender = async (ctx, req) => ({
                auth: { token: 'bearer xyz' }
            });

            const options = {
                env: { API_KEY: 'secret' },
                config: { providers: { test: {} } },
                app: { name: 'TestApp', version: '2.0' },
                state: { sessionId: 'sess-456' },
                request: mockRequest
            };

            const result = await ContextBuilder.build(options, [authExtender]);

            expect(result.env.API_KEY).toBe('secret');
            expect(result.config.providers.test).toEqual({});
            expect(result.app.name).toBe('TestApp');
            expect(result.state.sessionId).toBe('sess-456');
            expect(result.request).toBe(mockRequest);
            expect(result.auth.token).toBe('bearer xyz');
        });
    });
});
