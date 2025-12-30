/**
 * Unit tests for vault_file env-store module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 * - Log verification (hyper-observability)
 */
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { EnvStore } from '../src/env-store';
import { EnvKeyNotFoundError } from '../src/validators';
import { createTempEnvFile, cleanupTempFile, createLoggerSpy, expectLogContains } from './helpers/test-utils';
describe('EnvStore Module', () => {
    let tempFilePath = null;
    const originalEnv = process.env;
    beforeEach(() => {
        // Reset EnvStore singleton
        EnvStore.instance = undefined;
        // Reset process.env
        process.env = { ...originalEnv };
    });
    afterEach(() => {
        if (tempFilePath) {
            cleanupTempFile(tempFilePath);
            tempFilePath = null;
        }
        process.env = originalEnv;
    });
    // =========================================================================
    // Statement Coverage
    // =========================================================================
    describe('Statement Coverage', () => {
        it('should return singleton instance', () => {
            const instance1 = EnvStore.getInstance();
            const instance2 = EnvStore.getInstance();
            expect(instance1).toBe(instance2);
        });
        it('should initialize store on startup', async () => {
            tempFilePath = createTempEnvFile('TEST_KEY=test_value');
            const result = await EnvStore.onStartup(tempFilePath);
            expect(result.totalVarsLoaded).toBeGreaterThan(0);
            expect(EnvStore.isInitialized()).toBe(true);
        });
        it('should get value from store', async () => {
            tempFilePath = createTempEnvFile('STORE_KEY=store_value');
            await EnvStore.onStartup(tempFilePath);
            const value = EnvStore.get('STORE_KEY');
            expect(value).toBe('store_value');
        });
    });
    // =========================================================================
    // Branch Coverage
    // =========================================================================
    describe('Branch Coverage', () => {
        it('should prioritize process.env over internal store', async () => {
            process.env.PRIORITY_KEY = 'from_environ';
            tempFilePath = createTempEnvFile('PRIORITY_KEY=from_store');
            await EnvStore.onStartup(tempFilePath);
            const value = EnvStore.get('PRIORITY_KEY');
            // Node.js EnvStore prioritizes process.env
            expect(value).toBe('from_environ');
        });
        it('should fallback to internal store when not in process.env', async () => {
            delete process.env.FILE_ONLY_KEY;
            tempFilePath = createTempEnvFile('FILE_ONLY_KEY=file_value');
            await EnvStore.onStartup(tempFilePath);
            const value = EnvStore.get('FILE_ONLY_KEY');
            expect(value).toBe('file_value');
        });
        it('should return default when key not found', async () => {
            await EnvStore.onStartup('/nonexistent/.env');
            const value = EnvStore.get('NONEXISTENT_KEY', 'default_value');
            expect(value).toBe('default_value');
        });
        it('should return undefined when no default provided', async () => {
            await EnvStore.onStartup('/nonexistent/.env');
            const value = EnvStore.get('NONEXISTENT_KEY');
            expect(value).toBeUndefined();
        });
        it('should handle nonexistent env file gracefully', async () => {
            await EnvStore.onStartup('/nonexistent/.env');
            expect(EnvStore.isInitialized()).toBe(true);
        });
        it('should load vars from existing file', async () => {
            tempFilePath = createTempEnvFile('FILE_KEY=file_value');
            await EnvStore.onStartup(tempFilePath);
            expect(EnvStore.get('FILE_KEY')).toBe('file_value');
        });
    });
    // =========================================================================
    // Boundary Values
    // =========================================================================
    describe('Boundary Values', () => {
        it('should handle empty env file', async () => {
            tempFilePath = createTempEnvFile('');
            await EnvStore.onStartup(tempFilePath);
            expect(EnvStore.isInitialized()).toBe(true);
        });
        it('should store key with empty value', async () => {
            tempFilePath = createTempEnvFile('EMPTY_KEY=');
            await EnvStore.onStartup(tempFilePath);
            const value = EnvStore.get('EMPTY_KEY');
            expect(value).toBe('');
        });
    });
    // =========================================================================
    // Error Handling
    // =========================================================================
    describe('Error Handling', () => {
        it('should throw EnvKeyNotFoundError for missing required key', async () => {
            await EnvStore.onStartup('/nonexistent/.env');
            expect(() => {
                EnvStore.getOrThrow('MISSING_KEY');
            }).toThrow(EnvKeyNotFoundError);
        });
        it('should return value when key exists in getOrThrow', async () => {
            tempFilePath = createTempEnvFile('REQUIRED_KEY=required_value');
            await EnvStore.onStartup(tempFilePath);
            const value = EnvStore.getOrThrow('REQUIRED_KEY');
            expect(value).toBe('required_value');
        });
        it('should return process.env value in getOrThrow', async () => {
            process.env.ENV_REQUIRED = 'env_value';
            await EnvStore.onStartup('/nonexistent/.env');
            const value = EnvStore.getOrThrow('ENV_REQUIRED');
            expect(value).toBe('env_value');
        });
    });
    // =========================================================================
    // Log Verification
    // =========================================================================
    describe('Log Verification', () => {
        it('should log initialization start', async () => {
            const { logs, mockLogger } = createLoggerSpy();
            tempFilePath = createTempEnvFile('KEY=value');
            await EnvStore.onStartup(tempFilePath, mockLogger);
            expectLogContains(logs, 'info', 'Starting EnvStore initialization');
        });
        it('should log initialization complete', async () => {
            const { logs, mockLogger } = createLoggerSpy();
            tempFilePath = createTempEnvFile('KEY=value');
            await EnvStore.onStartup(tempFilePath, mockLogger);
            expectLogContains(logs, 'info', 'EnvStore initialized');
        });
        it('should log warning when file not found', async () => {
            const { logs, mockLogger } = createLoggerSpy();
            await EnvStore.onStartup('/nonexistent/path/.env', mockLogger);
            expectLogContains(logs, 'warn', 'not found');
        });
        it('should log error on getOrThrow failure', async () => {
            const { logs, mockLogger } = createLoggerSpy();
            await EnvStore.onStartup('/nonexistent/.env', mockLogger);
            try {
                EnvStore.getOrThrow('MISSING');
            }
            catch {
                // Expected
            }
            expectLogContains(logs, 'error', 'missing');
        });
    });
    // =========================================================================
    // Integration
    // =========================================================================
    describe('Integration', () => {
        it('should handle full workflow', async () => {
            process.env.SYSTEM_VAR = 'system_value';
            tempFilePath = createTempEnvFile(`# Database config
DATABASE_URL=postgres://localhost/db
API_KEY="secret-api-key"
DEBUG=true
`);
            const result = await EnvStore.onStartup(tempFilePath);
            expect(result.totalVarsLoaded).toBeGreaterThan(0);
            expect(EnvStore.isInitialized()).toBe(true);
            expect(EnvStore.get('DATABASE_URL')).toBe('postgres://localhost/db');
            expect(EnvStore.get('API_KEY')).toBe('secret-api-key');
            expect(EnvStore.get('DEBUG')).toBe('true');
            expect(EnvStore.get('SYSTEM_VAR')).toBe('system_value');
            expect(EnvStore.get('MISSING', 'default')).toBe('default');
            expect(EnvStore.getOrThrow('DATABASE_URL')).toBe('postgres://localhost/db');
        });
    });
});
//# sourceMappingURL=env-store.test.js.map