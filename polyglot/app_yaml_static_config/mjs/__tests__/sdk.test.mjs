/**
 * Unit tests for app-yaml-static-config SDK module.
 *
 * Tests cover:
 * - SDK initialization methods
 * - Read-only data access
 * - JSON serialization safety
 * - Provider/Service/Storage listing
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
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

describe('AppYamlConfigSDK', () => {
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
        it('should initialize SDK from directory', async () => {
            const sdk = await AppYamlConfigSDK.fromDirectory(FIXTURES_DIR);

            expect(sdk).toBeDefined();
            expect(sdk).toBeInstanceOf(AppYamlConfigSDK);
        });

        it('should return JSON-safe value with get()', async () => {
            const sdk = await AppYamlConfigSDK.fromDirectory(FIXTURES_DIR);

            const result = sdk.get('app');

            expect(result).toBeDefined();
            expect(result.name).toBe('test-app');
        });

        it('should return JSON-safe nested value', async () => {
            const sdk = await AppYamlConfigSDK.fromDirectory(FIXTURES_DIR);

            const result = sdk.getNested(['app', 'name']);

            expect(result).toBe('test-app');
        });

        it('should return complete config with getAll()', async () => {
            const sdk = await AppYamlConfigSDK.fromDirectory(FIXTURES_DIR);

            const result = sdk.getAll();

            expect(result).toBeDefined();
            expect(result.app).toBeDefined();
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('Branch Coverage', () => {
        it('should return provider names with listProviders()', async () => {
            const sdk = await AppYamlConfigSDK.fromDirectory(FIXTURES_DIR);

            const providers = sdk.listProviders();

            expect(Array.isArray(providers)).toBe(true);
            expect(providers).toContain('anthropic');
            expect(providers).toContain('openai');
        });

        it('should return service names with listServices()', async () => {
            const sdk = await AppYamlConfigSDK.fromDirectory(FIXTURES_DIR);

            const services = sdk.listServices();

            expect(Array.isArray(services)).toBe(true);
            expect(services).toContain('database');
            expect(services).toContain('cache');
        });

        it('should return storage names with listStorages()', async () => {
            const sdk = await AppYamlConfigSDK.fromDirectory(FIXTURES_DIR);

            const storages = sdk.listStorages();

            expect(Array.isArray(storages)).toBe(true);
            expect(storages).toContain('local');
            expect(storages).toContain('s3');
        });
    });

    // =========================================================================
    // Boundary Values
    // =========================================================================

    describe('Boundary Values', () => {
        it('should return undefined for missing key', async () => {
            const sdk = await AppYamlConfigSDK.fromDirectory(FIXTURES_DIR);

            const result = sdk.get('nonexistent_key');

            expect(result).toBeUndefined();
        });

        it('should return empty array when no providers defined', async () => {
            // Initialize with empty config
            const options = {
                files: [path.join(FIXTURES_DIR, 'empty.yaml')],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const sdk = new AppYamlConfigSDK(AppYamlConfig.getInstance());

            const providers = sdk.listProviders();

            expect(providers).toEqual([]);
        });
    });

    // =========================================================================
    // Integration
    // =========================================================================

    describe('Integration', () => {
        it('should reflect merged config from multiple files', async () => {
            // Initialize with multiple files
            const options = {
                files: [
                    path.join(FIXTURES_DIR, 'base.yaml'),
                    path.join(FIXTURES_DIR, 'override.yaml'),
                ],
                configDir: FIXTURES_DIR,
            };
            await AppYamlConfig.initialize(options);
            const sdk = new AppYamlConfigSDK(AppYamlConfig.getInstance());

            const appConfig = sdk.get('app');

            expect(appConfig.environment).toBe('production'); // From override
            expect(appConfig.name).toBe('test-app'); // From base
        });

        it('should return immutable values', async () => {
            const sdk = await AppYamlConfigSDK.fromDirectory(FIXTURES_DIR);

            // Get and modify
            const config = sdk.getAll();
            config.app.name = 'modified';

            // Get again - should be unchanged
            const config2 = sdk.getAll();

            expect(config2.app.name).toBe('test-app');
        });
    });
});
