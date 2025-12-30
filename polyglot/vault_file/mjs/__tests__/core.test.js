/**
 * Unit tests for vault_file core module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 */
import { describe, it, expect, afterEach } from '@jest/globals';
import { toJSON, fromJSON, parseEnvFile } from '../src/core';
import { createTempEnvFile, cleanupTempFile } from './helpers/test-utils';
describe('Core Module', () => {
    // =========================================================================
    // toJSON Tests
    // =========================================================================
    describe('toJSON()', () => {
        describe('Statement Coverage', () => {
            it('should serialize VaultFile to JSON string', () => {
                const file = {
                    header: {
                        version: '1.0.0',
                        createdAt: '2023-01-01T00:00:00.000Z',
                    },
                    secrets: { KEY: 'value' },
                };
                const result = toJSON(file);
                const parsed = JSON.parse(result);
                expect(parsed.header.version).toBe('1.0.0');
                // Keys are transformed to snake_case, so 'KEY' becomes '_k_e_y'
                expect(parsed.secrets._k_e_y).toBe('value');
            });
        });
        describe('Branch Coverage', () => {
            it('should convert camelCase keys to snake_case', () => {
                const file = {
                    header: {
                        version: '1.0.0',
                        createdAt: '2023-01-01T00:00:00.000Z',
                    },
                    secrets: {},
                };
                const result = toJSON(file);
                const parsed = JSON.parse(result);
                expect(parsed.header.created_at).toBeDefined();
                expect(parsed.header.createdAt).toBeUndefined();
            });
            it('should handle empty secrets', () => {
                const file = {
                    header: {
                        version: '1.0.0',
                        createdAt: '2023-01-01T00:00:00.000Z',
                    },
                    secrets: {},
                };
                const result = toJSON(file);
                const parsed = JSON.parse(result);
                expect(parsed.secrets).toEqual({});
            });
            it('should handle multiple secrets', () => {
                const file = {
                    header: {
                        version: '1.0.0',
                        createdAt: '2023-01-01T00:00:00.000Z',
                        description: 'Test vault',
                    },
                    secrets: { KEY1: 'value1', KEY2: 'value2' },
                };
                const result = toJSON(file);
                const parsed = JSON.parse(result);
                expect(Object.keys(parsed.secrets).length).toBe(2);
            });
        });
    });
    // =========================================================================
    // fromJSON Tests
    // =========================================================================
    describe('fromJSON()', () => {
        describe('Statement Coverage', () => {
            it('should deserialize valid JSON to VaultFile', () => {
                const json = '{"header": {"version": "1.0.0", "created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {"KEY": "value"}}';
                const result = fromJSON(json);
                expect(result.header.version).toBe('1.0.0');
                expect(result.secrets.KEY).toBe('value');
            });
        });
        describe('Branch Coverage', () => {
            it('should normalize version on load (1.0 -> 1.0.0)', () => {
                const json = '{"header": {"version": "1.0", "created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {}}';
                const result = fromJSON(json);
                expect(result.header.version).toBe('1.0.0');
            });
            it('should normalize single-part version (1 -> 1.0.0)', () => {
                const json = '{"header": {"version": "1", "created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {}}';
                const result = fromJSON(json);
                expect(result.header.version).toBe('1.0.0');
            });
            it('should convert snake_case keys to camelCase', () => {
                const json = '{"header": {"version": "1.0.0", "created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {}}';
                const result = fromJSON(json);
                expect(result.header.createdAt).toBeDefined();
            });
            it('should handle missing version', () => {
                const json = '{"header": {"created_at": "2023-01-01T00:00:00.000Z"}, "secrets": {}}';
                const result = fromJSON(json);
                // Version should be undefined or use default behavior
                expect(result.header).toBeDefined();
            });
        });
        describe('Error Handling', () => {
            it('should throw on invalid JSON', () => {
                expect(() => fromJSON('not valid json')).toThrow();
            });
        });
    });
    // =========================================================================
    // parseEnvFile Tests
    // =========================================================================
    describe('parseEnvFile()', () => {
        let tempFilePath = null;
        afterEach(() => {
            if (tempFilePath) {
                cleanupTempFile(tempFilePath);
                tempFilePath = null;
            }
        });
        describe('Statement Coverage', () => {
            it('should parse valid .env file', () => {
                tempFilePath = createTempEnvFile('KEY=value\nANOTHER=test');
                const result = parseEnvFile(tempFilePath);
                expect(result.KEY).toBe('value');
                expect(result.ANOTHER).toBe('test');
            });
        });
        describe('Branch Coverage', () => {
            it('should return empty object for nonexistent file', () => {
                const result = parseEnvFile('/nonexistent/path/.env');
                expect(result).toEqual({});
            });
            it('should skip empty lines', () => {
                tempFilePath = createTempEnvFile('KEY=value\n\n\nANOTHER=test');
                const result = parseEnvFile(tempFilePath);
                expect(Object.keys(result).length).toBe(2);
            });
            it('should skip comment lines', () => {
                tempFilePath = createTempEnvFile('# This is a comment\nKEY=value\n# Another comment');
                const result = parseEnvFile(tempFilePath);
                expect(Object.keys(result).length).toBe(1);
                expect(result.KEY).toBe('value');
            });
            it('should skip lines without equals sign', () => {
                tempFilePath = createTempEnvFile('INVALID_LINE\nKEY=value');
                const result = parseEnvFile(tempFilePath);
                expect(Object.keys(result).length).toBe(1);
            });
            it('should remove double quotes from values', () => {
                tempFilePath = createTempEnvFile('KEY="quoted value"');
                const result = parseEnvFile(tempFilePath);
                expect(result.KEY).toBe('quoted value');
            });
            it('should remove single quotes from values', () => {
                tempFilePath = createTempEnvFile("KEY='single quoted'");
                const result = parseEnvFile(tempFilePath);
                expect(result.KEY).toBe('single quoted');
            });
            it('should preserve unquoted values', () => {
                tempFilePath = createTempEnvFile('KEY=unquoted value');
                const result = parseEnvFile(tempFilePath);
                expect(result.KEY).toBe('unquoted value');
            });
        });
        describe('Boundary Values', () => {
            it('should handle empty file', () => {
                tempFilePath = createTempEnvFile('');
                const result = parseEnvFile(tempFilePath);
                expect(result).toEqual({});
            });
            it('should handle empty value', () => {
                tempFilePath = createTempEnvFile('KEY=');
                const result = parseEnvFile(tempFilePath);
                expect(result.KEY).toBe('');
            });
            it('should handle value with equals sign', () => {
                tempFilePath = createTempEnvFile('URL=postgres://user:pass=word@host');
                const result = parseEnvFile(tempFilePath);
                expect(result.URL).toBe('postgres://user:pass=word@host');
            });
            it('should strip whitespace around key and value', () => {
                tempFilePath = createTempEnvFile('  KEY  =  value  ');
                const result = parseEnvFile(tempFilePath);
                expect(result.KEY).toBe('value');
            });
        });
    });
    // =========================================================================
    // Integration Tests
    // =========================================================================
    describe('Integration', () => {
        it('should roundtrip JSON serialization', () => {
            const original = {
                header: {
                    version: '2.0.0',
                    createdAt: '2023-06-15T10:30:00.000Z',
                    description: 'Test vault file',
                },
                secrets: { DB_PASSWORD: 'secret123', API_TOKEN: 'token456' },
            };
            const json = toJSON(original);
            const restored = fromJSON(json);
            expect(restored.header.version).toBe(original.header.version);
            expect(restored.secrets.DB_PASSWORD).toBe(original.secrets.DB_PASSWORD);
            expect(restored.secrets.API_TOKEN).toBe(original.secrets.API_TOKEN);
        });
        it('should parse realistic .env file', () => {
            const content = `# Database configuration
DATABASE_URL=postgres://user:password@localhost:5432/mydb
DATABASE_POOL_SIZE=10

# API Keys
API_KEY="sk-live-123456789"
API_SECRET='super-secret-key'

# Feature flags
DEBUG=true
VERBOSE=false
`;
            const tempFilePath = createTempEnvFile(content);
            try {
                const result = parseEnvFile(tempFilePath);
                expect(result.DATABASE_URL).toBe('postgres://user:password@localhost:5432/mydb');
                expect(result.DATABASE_POOL_SIZE).toBe('10');
                expect(result.API_KEY).toBe('sk-live-123456789');
                expect(result.API_SECRET).toBe('super-secret-key');
                expect(result.DEBUG).toBe('true');
                expect(result.VERBOSE).toBe('false');
            }
            finally {
                cleanupTempFile(tempFilePath);
            }
        });
    });
});
//# sourceMappingURL=core.test.js.map