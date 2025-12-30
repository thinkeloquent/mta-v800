/**
 * Unit tests for app-yaml-static-config core module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 * - Log verification (hyper-observability)
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { AppYamlConfig } from '../dist/core.js';
import { ImmutabilityError } from '../dist/validators.js';
import { createLoggerSpy, expectLogContains } from './helpers/logger-spy.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, '..', '..', '__fixtures__');

// Helper to reset singleton
function resetSingleton() {
    // Access private static field for testing
    AppYamlConfig._instance = null;
}

describe('AppYamlConfig', () => {
    beforeEach(() => {
        resetSingleton();
    });

    afterEach(() => {
        resetSingleton();
    });

    // =========================================================================
    // Statement Coverage
    // =========================================================================

    describe('Statement Coverage', () => {
        it('should create singleton on initialize', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };

            const instance = await AppYamlConfig.initialize(options);

            expect(instance).toBeDefined();
            expect(instance).toBeInstanceOf(AppYamlConfig);
        });

        it('should return same instance on getInstance', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };

            const instance1 = await AppYamlConfig.initialize(options);
            const instance2 = AppYamlConfig.getInstance();

            expect(instance1).toBe(instance2);
        });

        it('should return top-level value with get()', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const appConfig = instance.get('app');

            expect(appConfig).toBeDefined();
            expect(appConfig.name).toBe('test-app');
        });

        it('should return nested value with getNested()', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const value = instance.getNested(['app', 'name']);

            expect(value).toBe('test-app');
        });

        it('should return deep copy with getAll()', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const config1 = instance.getAll();
            const config2 = instance.getAll();

            expect(config1).toEqual(config2);
            expect(config1).not.toBe(config2);
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('Branch Coverage', () => {
        it('should return existing instance when already initialized', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };

            const instance1 = await AppYamlConfig.initialize(options);
            const instance2 = await AppYamlConfig.initialize(options);

            expect(instance1).toBe(instance2);
        });

        it('should return default when key missing in get()', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const result = instance.get('nonexistent', 'default_value');

            expect(result).toBe('default_value');
        });

        it('should return default when path missing in getNested()', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const result = instance.getNested(['app', 'nonexistent', 'path'], 'fallback');

            expect(result).toBe('fallback');
        });

        it('should return original config for specific file', async () => {
            const basePath = path.join(FIXTURES_DIR, 'base.yaml');
            const options = {
                files: [basePath],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const original = instance.getOriginal(basePath);

            expect(original).toBeDefined();
            expect(original.app).toBeDefined();
        });

        it('should return undefined when getOriginal called without file', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const original = instance.getOriginal();

            expect(original).toBeUndefined();
        });
    });

    // =========================================================================
    // Boundary Values
    // =========================================================================

    describe('Boundary Values', () => {
        it('should handle empty config file', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'empty.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const config = instance.getAll();

            expect(config).toEqual({});
        });

        it('should handle deeply nested config', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'nested.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const value = instance.getNested(['deeply', 'nested', 'config', 'value']);

            expect(value).toBe('found');
        });

        it('should handle empty keys array in getNested()', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const result = instance.getNested([], 'empty_default');

            // With empty keys, should return the entire config
            expect(result).toBeDefined();
        });
    });

    // =========================================================================
    // Error Handling
    // =========================================================================

    describe('Error Handling', () => {
        it('should throw when getInstance called before initialize', () => {
            expect(() => AppYamlConfig.getInstance()).toThrow('not initialized');
        });

        it('should throw when loading nonexistent file', async () => {
            const options = {
                files: ['/nonexistent/path/config.yaml'],
                configDir: FIXTURES_DIR,
            };

            await expect(AppYamlConfig.initialize(options)).rejects.toThrow();
        });

        it('should throw ImmutabilityError on set()', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            expect(() => instance.set('key', 'value')).toThrow(ImmutabilityError);
        });

        it('should throw ImmutabilityError on update()', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            expect(() => instance.update({ key: 'value' })).toThrow(ImmutabilityError);
        });

        it('should throw ImmutabilityError on reset()', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            expect(() => instance.reset()).toThrow(ImmutabilityError);
        });

        it('should throw ImmutabilityError on clear()', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            expect(() => instance.clear()).toThrow(ImmutabilityError);
        });
    });

    // =========================================================================
    // Log Verification
    // =========================================================================

    describe('Log Verification', () => {
        it('should log info when initializing', async () => {
            const { logs, mockLogger } = createLoggerSpy();
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
                logger: mockLogger,
            };

            await AppYamlConfig.initialize(options);

            expectLogContains(logs, 'info', 'Initializing configuration');
        });

        it('should log debug when loading files', async () => {
            const { logs, mockLogger } = createLoggerSpy();
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
                logger: mockLogger,
            };

            await AppYamlConfig.initialize(options);

            expectLogContains(logs, 'debug', 'Loading config file');
        });
    });

    // =========================================================================
    // Integration
    // =========================================================================

    describe('Integration', () => {
        it('should merge multiple config files correctly', async () => {
            const options = {
                files: [
                    path.join(FIXTURES_DIR, 'base.yaml'),
                    path.join(FIXTURES_DIR, 'override.yaml'),
                ],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            // Override should take precedence
            const appEnv = instance.getNested(['app', 'environment']);
            expect(appEnv).toBe('production');

            // Base values should be preserved
            const appName = instance.getNested(['app', 'name']);
            expect(appName).toBe('test-app');

            // Override should add new keys
            const appDebug = instance.getNested(['app', 'debug']);
            expect(appDebug).toBe(false);
        });

        it('should restore config to initial state', async () => {
            const options = {
                files: [path.join(FIXTURES_DIR, 'base.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const initialConfig = instance.getAll();
            instance.restore();
            const restoredConfig = instance.getAll();

            expect(restoredConfig).toEqual(initialConfig);
        });

        it('should return all original configs', async () => {
            const basePath = path.join(FIXTURES_DIR, 'base.yaml');
            const overridePath = path.join(FIXTURES_DIR, 'override.yaml');
            const options = {
                files: [basePath, overridePath],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const instance = AppYamlConfig.getInstance();

            const originals = instance.getOriginalAll();

            expect(originals.size).toBe(2);
            expect(originals.has(basePath)).toBe(true);
            expect(originals.has(overridePath)).toBe(true);
        });
    });
});
