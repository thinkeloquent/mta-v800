/**
 * Unit tests for vault_file validators module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 */
import { describe, it, expect } from '@jest/globals';
import { EnvKeyNotFoundError } from '../src/validators';

describe('Validators Module', () => {
    // =========================================================================
    // EnvKeyNotFoundError Tests
    // =========================================================================

    describe('EnvKeyNotFoundError', () => {
        describe('Statement Coverage', () => {
            it('should create error with key name in message', () => {
                const error = new EnvKeyNotFoundError('MY_KEY');

                expect(error.message).toContain('MY_KEY');
            });

            it('should set error name correctly', () => {
                const error = new EnvKeyNotFoundError('KEY');

                expect(error.name).toBe('EnvKeyNotFoundError');
            });
        });

        describe('Branch Coverage', () => {
            it('should handle simple key name', () => {
                const error = new EnvKeyNotFoundError('KEY');

                expect(error.message).toContain('KEY');
            });

            it('should handle key with underscores', () => {
                const error = new EnvKeyNotFoundError('MY_LONG_KEY_NAME');

                expect(error.message).toContain('MY_LONG_KEY_NAME');
            });
        });

        describe('Boundary Values', () => {
            it('should handle empty key', () => {
                const error = new EnvKeyNotFoundError('');

                expect(error.name).toBe('EnvKeyNotFoundError');
                expect(error.message).toContain('not found');
            });

            it('should handle key with special characters', () => {
                const error = new EnvKeyNotFoundError('KEY-WITH-DASHES');

                expect(error.message).toContain('KEY-WITH-DASHES');
            });

            it('should handle key with numbers', () => {
                const error = new EnvKeyNotFoundError('KEY123');

                expect(error.message).toContain('KEY123');
            });
        });

        describe('Error Handling', () => {
            it('should be instance of Error', () => {
                const error = new EnvKeyNotFoundError('KEY');

                expect(error).toBeInstanceOf(Error);
            });

            it('should be throwable and catchable', () => {
                expect(() => {
                    throw new EnvKeyNotFoundError('TEST_KEY');
                }).toThrow(EnvKeyNotFoundError);
            });

            it('should be catchable as base Error', () => {
                try {
                    throw new EnvKeyNotFoundError('MY_KEY');
                } catch (e) {
                    expect(e).toBeInstanceOf(Error);
                    expect((e as Error).message).toContain('MY_KEY');
                }
            });

            it('should have correct stack trace', () => {
                const error = new EnvKeyNotFoundError('KEY');

                expect(error.stack).toBeDefined();
                expect(error.stack).toContain('EnvKeyNotFoundError');
            });
        });

        describe('Message Format', () => {
            it('should include "not found" in message', () => {
                const error = new EnvKeyNotFoundError('DATABASE_URL');

                expect(error.message.toLowerCase()).toContain('not found');
            });

            it('should include "environment variable" in message', () => {
                const error = new EnvKeyNotFoundError('API_KEY');

                expect(error.message.toLowerCase()).toContain('environment variable');
            });
        });
    });
});
