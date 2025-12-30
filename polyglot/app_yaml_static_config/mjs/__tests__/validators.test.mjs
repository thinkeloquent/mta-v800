/**
 * Unit tests for app-yaml-static-config validators module.
 *
 * Tests cover:
 * - Error class instantiation
 * - Error message formatting
 * - Validation function behavior
 */
import { describe, it, expect } from 'vitest';
import {
    ConfigurationError,
    ImmutabilityError,
    validateConfigKey,
} from '../dist/validators.js';

describe('ConfigurationError', () => {
    describe('Statement Coverage', () => {
        it('should accept message only', () => {
            const error = new ConfigurationError('Test error');

            expect(error.message).toContain('Test error');
            expect(error.name).toBe('ConfigurationError');
        });

        it('should include context in message', () => {
            const error = new ConfigurationError('Test error', { key: 'value' });

            expect(error.message).toContain('Test error');
            expect(error.message).toContain('context');
        });
    });

    describe('Branch Coverage', () => {
        it('should store context property', () => {
            const context = { file: 'test.yaml', line: 42 };
            const error = new ConfigurationError('Parse error', context);

            expect(error.context).toEqual(context);
        });

        it('should have undefined context by default', () => {
            const error = new ConfigurationError('Test error');

            expect(error.context).toBeUndefined();
        });
    });
});

describe('ImmutabilityError', () => {
    describe('Statement Coverage', () => {
        it('should be instance of ConfigurationError', () => {
            const error = new ImmutabilityError('Cannot modify');

            expect(error).toBeInstanceOf(ConfigurationError);
            expect(error).toBeInstanceOf(Error);
        });

        it('should format message correctly', () => {
            const error = new ImmutabilityError('Configuration is immutable');

            expect(error.message).toContain('Configuration is immutable');
            expect(error.name).toBe('ImmutabilityError');
        });
    });
});

describe('validateConfigKey', () => {
    describe('Statement Coverage', () => {
        it('should not throw for valid key', () => {
            expect(() => validateConfigKey('valid_key')).not.toThrow();
        });
    });

    describe('Branch Coverage', () => {
        it('should throw for empty string', () => {
            expect(() => validateConfigKey('')).toThrow(ConfigurationError);
        });

        it('should throw for null', () => {
            expect(() => validateConfigKey(null)).toThrow(ConfigurationError);
        });

        it('should throw for undefined', () => {
            expect(() => validateConfigKey(undefined)).toThrow(ConfigurationError);
        });
    });

    describe('Boundary Values', () => {
        it('should accept single character key', () => {
            expect(() => validateConfigKey('a')).not.toThrow();
        });

        it('should accept whitespace-only key', () => {
            // Current implementation treats whitespace as truthy
            expect(() => validateConfigKey('   ')).not.toThrow();
        });
    });
});
