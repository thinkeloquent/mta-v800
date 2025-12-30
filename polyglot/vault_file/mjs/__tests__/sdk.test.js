/**
 * Unit tests for vault_file SDK module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 */
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { VaultFileSDK, VaultFileSDKBuilder } from '../src/sdk';
import { EnvStore } from '../src/env-store';
import { createTempEnvFile, cleanupTempFile } from './helpers/test-utils';
describe('SDK Module', () => {
    let tempFilePath = null;
    beforeEach(() => {
        // Reset EnvStore singleton
        EnvStore.instance = undefined;
    });
    afterEach(() => {
        if (tempFilePath) {
            cleanupTempFile(tempFilePath);
            tempFilePath = null;
        }
    });
    // =========================================================================
    // VaultFileSDK Tests
    // =========================================================================
    describe('VaultFileSDK', () => {
        describe('Statement Coverage', () => {
            it('should create builder via static create()', () => {
                const builder = VaultFileSDK.create();
                expect(builder).toBeInstanceOf(VaultFileSDKBuilder);
            });
            it('should build SDK instance', () => {
                const sdk = VaultFileSDK.create().build();
                expect(sdk).toBeInstanceOf(VaultFileSDK);
            });
            it('should load config and return result', async () => {
                tempFilePath = createTempEnvFile('KEY=value');
                const sdk = VaultFileSDK.create().withEnvPath(tempFilePath).build();
                const result = await sdk.loadConfig();
                expect(result.success).toBe(true);
                expect(result.data).toBeDefined();
            });
        });
        describe('Branch Coverage', () => {
            it('should succeed for loadFromPath with existing file', async () => {
                tempFilePath = createTempEnvFile('KEY1=val1\nKEY2=val2');
                const sdk = VaultFileSDK.create().build();
                const result = await sdk.loadFromPath(tempFilePath);
                expect(result.success).toBe(true);
                expect(result.data?.totalVarsLoaded).toBe(2);
            });
            it('should fail for loadFromPath with missing file', async () => {
                const sdk = VaultFileSDK.create().build();
                const result = await sdk.loadFromPath('/nonexistent/path/.env');
                expect(result.success).toBe(false);
                expect(result.error?.code).toBe('FILE_NOT_FOUND');
            });
            it('should succeed for validateFile with valid file', async () => {
                tempFilePath = createTempEnvFile('VALID_KEY=value');
                const sdk = VaultFileSDK.create().build();
                const result = await sdk.validateFile(tempFilePath);
                expect(result.success).toBe(true);
                expect(result.data?.valid).toBe(true);
                expect(result.data?.errors).toEqual([]);
            });
            it('should fail for validateFile with missing file', async () => {
                const sdk = VaultFileSDK.create().build();
                const result = await sdk.validateFile('/nonexistent/.env');
                expect(result.success).toBe(false);
                expect(result.error?.code).toBe('FILE_NOT_FOUND');
            });
            it('should return not implemented for exportToFormat', async () => {
                const sdk = VaultFileSDK.create().build();
                const result = await sdk.exportToFormat('json', '/some/path');
                expect(result.success).toBe(false);
                expect(result.error?.code).toBe('NOT_IMPLEMENTED');
            });
        });
    });
    // =========================================================================
    // Agent Operations Tests
    // =========================================================================
    describe('Agent Operations', () => {
        it('should return config description', async () => {
            tempFilePath = createTempEnvFile('KEY=value');
            const sdk = VaultFileSDK.create().withEnvPath(tempFilePath).build();
            await sdk.loadConfig();
            const result = sdk.describeConfig();
            expect(result.success).toBe(true);
            expect(result.data?.version).toBe('1.0.0');
            expect(result.data?.sources).toContain(tempFilePath);
        });
        it('should return masked secret info when exists', async () => {
            tempFilePath = createTempEnvFile('SECRET_KEY=secret_value');
            const sdk = VaultFileSDK.create().withEnvPath(tempFilePath).build();
            await sdk.loadConfig();
            const result = sdk.getSecretSafe('SECRET_KEY');
            expect(result.success).toBe(true);
            expect(result.data?.key).toBe('SECRET_KEY');
            expect(result.data?.exists).toBe(true);
            expect(result.data?.masked).toBe('***');
        });
        it('should indicate when secret does not exist', async () => {
            const sdk = VaultFileSDK.create().build();
            await EnvStore.onStartup('/nonexistent/.env');
            const result = sdk.getSecretSafe('NONEXISTENT_KEY');
            expect(result.success).toBe(true);
            expect(result.data?.exists).toBe(false);
        });
        it('should return empty list for listAvailableKeys', () => {
            const sdk = VaultFileSDK.create().build();
            const result = sdk.listAvailableKeys();
            expect(result.success).toBe(true);
            expect(result.data).toEqual([]);
        });
    });
    // =========================================================================
    // DEV Tool Operations Tests
    // =========================================================================
    describe('DEV Tool Operations', () => {
        it('should report initialized state in diagnose', async () => {
            tempFilePath = createTempEnvFile('KEY=value');
            const sdk = VaultFileSDK.create().withEnvPath(tempFilePath).build();
            await sdk.loadConfig();
            const result = sdk.diagnoseEnvStore();
            expect(result.success).toBe(true);
            expect(result.data?.initialized).toBe(true);
        });
        it('should report uninitialized state in diagnose', () => {
            // Reset singleton
            EnvStore.instance = undefined;
            const sdk = VaultFileSDK.create().build();
            const result = sdk.diagnoseEnvStore();
            expect(result.success).toBe(true);
            expect(result.data?.initialized).toBe(false);
        });
        it('should return empty when all required keys present', async () => {
            tempFilePath = createTempEnvFile('KEY1=val1\nKEY2=val2');
            const sdk = VaultFileSDK.create().withEnvPath(tempFilePath).build();
            await sdk.loadConfig();
            const result = sdk.findMissingRequired(['KEY1', 'KEY2']);
            expect(result.success).toBe(true);
            expect(result.data).toEqual([]);
        });
        it('should return missing keys', async () => {
            tempFilePath = createTempEnvFile('KEY1=val1');
            const sdk = VaultFileSDK.create().withEnvPath(tempFilePath).build();
            await sdk.loadConfig();
            const result = sdk.findMissingRequired(['KEY1', 'KEY2', 'KEY3']);
            expect(result.success).toBe(true);
            expect(result.data).toContain('KEY2');
            expect(result.data).toContain('KEY3');
            expect(result.data).not.toContain('KEY1');
        });
        it('should return empty list for suggestMissingKeys', () => {
            const sdk = VaultFileSDK.create().build();
            const result = sdk.suggestMissingKeys('DB_');
            expect(result.success).toBe(true);
            expect(result.data).toEqual([]);
        });
    });
    // =========================================================================
    // Error Handling Tests
    // =========================================================================
    describe('Error Handling', () => {
        it('should handle loadConfig exception gracefully', async () => {
            const sdk = VaultFileSDK.create().withEnvPath('/invalid/path/.env').build();
            // Mock EnvStore.onStartup to throw
            const originalOnStartup = EnvStore.onStartup;
            EnvStore.onStartup = async () => {
                throw new Error('Forced error');
            };
            try {
                const result = await sdk.loadConfig();
                expect(result.success).toBe(false);
                expect(result.error?.code).toBe('LOAD_ERROR');
            }
            finally {
                EnvStore.onStartup = originalOnStartup;
            }
        });
    });
    // =========================================================================
    // VaultFileSDKBuilder Tests
    // =========================================================================
    describe('VaultFileSDKBuilder', () => {
        describe('Statement Coverage', () => {
            it('should set custom env path', () => {
                const sdk = VaultFileSDK.create()
                    .withEnvPath('/custom/.env')
                    .build();
                // Access private property for verification
                expect(sdk.envPath).toBe('/custom/.env');
            });
            it('should set base64 parsers', () => {
                const parsers = { json: (x) => JSON.parse(x) };
                const sdk = VaultFileSDK.create()
                    .withBase64Parsers(parsers)
                    .build();
                expect(sdk.base64Parsers).toHaveProperty('json');
            });
        });
        describe('Builder Chaining', () => {
            it('should support method chaining', () => {
                const sdk = VaultFileSDK.create()
                    .withEnvPath('/custom/.env')
                    .withBase64Parsers({ test: (x) => x })
                    .build();
                expect(sdk.envPath).toBe('/custom/.env');
                expect(sdk.base64Parsers).toHaveProperty('test');
            });
        });
    });
});
//# sourceMappingURL=sdk.test.js.map