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
import { createSampleConfig, createMockAppYamlConfig, createLoggerSpy } from './helpers/test-utils.mjs';

// Mock the external dependencies
vi.mock('app-yaml-static-config', () => ({
    AppYamlConfig: {
        getInstance: vi.fn()
    }
}));

vi.mock('runtime-template-resolver', () => ({
    createResolver: vi.fn(() => ({
        resolveObject: vi.fn(async (config) => config)
    })),
    ComputeScope: {
        STARTUP: 'STARTUP',
        REQUEST: 'REQUEST'
    }
}));

// Import after mocks are set up
import { ConfigSDK } from '../src/sdk.ts';
import { AppYamlConfig } from 'app-yaml-static-config';

describe('ConfigSDK', () => {
    beforeEach(() => {
        // Reset singleton before each test
        ConfigSDK.instance = undefined;

        // Reset mocks
        vi.clearAllMocks();

        // Suppress console output during tests
        vi.spyOn(console, 'log').mockImplementation(() => {});
        vi.spyOn(console, 'error').mockImplementation(() => {});
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    // =========================================================================
    // Statement Coverage
    // =========================================================================

    describe('Statement Coverage', () => {
        it('should create instance with initialize()', async () => {
            const mockConfig = createSampleConfig();
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => mockConfig
            });

            const sdk = await ConfigSDK.initialize({});

            expect(sdk).toBeInstanceOf(ConfigSDK);
        });

        it('should return raw config with getRaw()', async () => {
            const mockConfig = { key: 'value' };
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => mockConfig
            });

            const sdk = await ConfigSDK.initialize({});
            const raw = sdk.getRaw();

            expect(raw).toEqual(mockConfig);
        });

        it('should return JSON with toJSON()', async () => {
            const mockConfig = { data: 'value' };
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => mockConfig
            });

            const sdk = await ConfigSDK.initialize({});
            const json = await sdk.toJSON();

            expect(json).toEqual(mockConfig);
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('Branch Coverage', () => {
        it('should return existing instance on second initialize()', async () => {
            const mockConfig = { key: 'value' };
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => mockConfig
            });

            const sdk1 = await ConfigSDK.initialize({});
            const sdk2 = await ConfigSDK.initialize({});

            expect(sdk1).toBe(sdk2);
        });

        it('should throw when getInstance() called before initialize()', () => {
            expect(() => ConfigSDK.getInstance()).toThrow('not initialized');
        });

        it('should return instance with getInstance() after initialize()', async () => {
            const mockConfig = {};
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => mockConfig
            });

            await ConfigSDK.initialize({});
            const sdk = ConfigSDK.getInstance();

            expect(sdk).toBeInstanceOf(ConfigSDK);
        });
    });

    // =========================================================================
    // Boundary Values
    // =========================================================================

    describe('Boundary Values', () => {
        it('should handle empty config', async () => {
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => ({})
            });

            const sdk = await ConfigSDK.initialize({});

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
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => deepConfig
            });

            const sdk = await ConfigSDK.initialize({});

            expect(sdk.getRaw().level1.level2.level3.value).toBe('deep');
        });

        it('should handle config with null values', async () => {
            const configWithNulls = {
                nullValue: null,
                normalValue: 'test'
            };
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => configWithNulls
            });

            const sdk = await ConfigSDK.initialize({});

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

            await expect(sdk.getResolved('STARTUP')).rejects.toThrow('not initialized');
        });

        it('should handle context extenders', async () => {
            const mockConfig = { app: { name: 'Test' } };
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => mockConfig
            });

            const extender = async (ctx, req) => ({ custom: 'extended' });
            const sdk = await ConfigSDK.initialize({ contextExtenders: [extender] });

            expect(sdk).toBeInstanceOf(ConfigSDK);
        });
    });

    // =========================================================================
    // Log Verification
    // =========================================================================

    describe('Log Verification', () => {
        it('should log during bootstrap', async () => {
            const mockConfig = { key: 'value' };
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => mockConfig
            });

            await ConfigSDK.initialize({});

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
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => fullConfig
            });

            const sdk = await ConfigSDK.initialize({});

            expect(sdk.getRaw().app.name).toBe('IntegrationTest');
            expect(sdk.getRaw().providers.test.baseUrl).toBe('https://test.com');
        });

        it('should work with realistic provider config', async () => {
            const providerConfig = createSampleConfig();
            AppYamlConfig.getInstance.mockReturnValue({
                getAll: () => providerConfig
            });

            const sdk = await ConfigSDK.initialize({});
            const raw = sdk.getRaw();

            expect(raw.app.name).toBe('Test App');
            expect(raw.providers.test_provider.base_url).toBe('https://api.test.com');
        });
    });
});
