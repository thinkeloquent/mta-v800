/**
 * Unit tests for ConfigSDK class.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 * - Log verification (hyper-observability)
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { createSampleConfig } from './helpers/test-utils.mjs';
import { ConfigSDK, ComputeScope } from '../src/sdk.ts';

describe('ConfigSDK', () => {
    beforeEach(() => {
        // Reset singleton before each test
        ConfigSDK.resetInstance();

        // Suppress console output during tests
        vi.spyOn(console, 'log').mockImplementation(() => {});
        vi.spyOn(console, 'error').mockImplementation(() => {});
    });

    afterEach(() => {
        vi.restoreAllMocks();
        ConfigSDK.resetInstance();
    });

    // =========================================================================
    // Statement Coverage
    // =========================================================================

    describe('Statement Coverage', () => {
        it('should create instance with initialize()', async () => {
            const mockConfig = createSampleConfig();
            const sdk = await ConfigSDK.initialize({ config: mockConfig });

            expect(sdk).toBeInstanceOf(ConfigSDK);
        });

        it('should return raw config with getRaw()', async () => {
            const mockConfig = { key: 'value' };
            const sdk = await ConfigSDK.initialize({ config: mockConfig });
            const raw = sdk.getRaw();

            expect(raw).toEqual(mockConfig);
        });

        it('should return JSON with toJSON()', async () => {
            const mockConfig = { data: 'value' };
            const sdk = await ConfigSDK.initialize({ config: mockConfig });
            const json = await sdk.toJSON();

            expect(json).toEqual(mockConfig);
        });

        it('should work with configProvider', async () => {
            const mockConfig = { provider: 'test' };
            const configProvider = { getAll: () => mockConfig };
            const sdk = await ConfigSDK.initialize({ configProvider });
            const raw = sdk.getRaw();

            expect(raw).toEqual(mockConfig);
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('Branch Coverage', () => {
        it('should return existing instance on second initialize()', async () => {
            const mockConfig = { key: 'value' };

            const sdk1 = await ConfigSDK.initialize({ config: mockConfig });
            const sdk2 = await ConfigSDK.initialize({ config: { different: 'config' } });

            expect(sdk1).toBe(sdk2);
        });

        it('should throw when getInstance() called before initialize()', () => {
            expect(() => ConfigSDK.getInstance()).toThrow('not initialized');
        });

        it('should return instance with getInstance() after initialize()', async () => {
            await ConfigSDK.initialize({ config: {} });
            const sdk = ConfigSDK.getInstance();

            expect(sdk).toBeInstanceOf(ConfigSDK);
        });

        it('should use empty config when none provided', async () => {
            const sdk = await ConfigSDK.initialize({});

            expect(sdk.getRaw()).toEqual({});
        });
    });

    // =========================================================================
    // Boundary Values
    // =========================================================================

    describe('Boundary Values', () => {
        it('should handle empty config', async () => {
            const sdk = await ConfigSDK.initialize({ config: {} });

            expect(sdk.getRaw()).toEqual({});
        });

        it('should handle deeply nested config', async () => {
            const deepConfig = {
                level1: {
                    level2: {
                        level3: {
                            value: 'deep'
                        }
                    }
                }
            };
            const sdk = await ConfigSDK.initialize({ config: deepConfig });

            expect(sdk.getRaw().level1.level2.level3.value).toBe('deep');
        });

        it('should handle config with null values', async () => {
            const configWithNulls = {
                nullValue: null,
                normalValue: 'test'
            };
            const sdk = await ConfigSDK.initialize({ config: configWithNulls });

            expect(sdk.getRaw().nullValue).toBeNull();
            expect(sdk.getRaw().normalValue).toBe('test');
        });
    });

    // =========================================================================
    // Error Handling
    // =========================================================================

    describe('Error Handling', () => {
        it('should throw on getResolved() when not initialized', async () => {
            // Create SDK without bootstrapping
            const sdk = new ConfigSDK({});
            // sdk.initialized is false by default

            await expect(sdk.getResolved(ComputeScope.STARTUP)).rejects.toThrow('not initialized');
        });

        it('should handle context extenders', async () => {
            const mockConfig = { app: { name: 'Test' } };
            const extender = async (ctx, req) => ({ custom: 'extended' });
            const sdk = await ConfigSDK.initialize({
                config: mockConfig,
                contextExtenders: [extender]
            });

            expect(sdk).toBeInstanceOf(ConfigSDK);
        });
    });

    // =========================================================================
    // Log Verification
    // =========================================================================

    describe('Log Verification', () => {
        it('should log during bootstrap', async () => {
            const mockConfig = { key: 'value' };
            await ConfigSDK.initialize({ config: mockConfig });

            // Logger outputs to console.log
            expect(console.log).toHaveBeenCalled();
        });
    });

    // =========================================================================
    // Integration Tests
    // =========================================================================

    describe('Integration', () => {
        it('should complete full initialization flow', async () => {
            const fullConfig = {
                app: { name: 'IntegrationTest', version: '1.0.0' },
                providers: {
                    test: { baseUrl: 'https://test.com' }
                }
            };
            const sdk = await ConfigSDK.initialize({ config: fullConfig });

            expect(sdk.getRaw().app.name).toBe('IntegrationTest');
            expect(sdk.getRaw().providers.test.baseUrl).toBe('https://test.com');
        });

        it('should work with realistic provider config', async () => {
            const providerConfig = createSampleConfig();
            const sdk = await ConfigSDK.initialize({ config: providerConfig });
            const raw = sdk.getRaw();

            expect(raw.app.name).toBe('Test App');
            expect(raw.providers.test_provider.base_url).toBe('https://api.test.com');
        });

        it('should apply overwrites in getResolved()', async () => {
            const config = {
                app: { name: 'Test' },
                database: { host: 'localhost', password: null },
                overwrite_from_context: {
                    database: { password: 'secret123' }
                }
            };
            const sdk = await ConfigSDK.initialize({ config });
            const resolved = await sdk.getResolved(ComputeScope.STARTUP);

            expect(resolved.database.password).toBe('secret123');
            expect(resolved.database.host).toBe('localhost');
        });
    });
});
