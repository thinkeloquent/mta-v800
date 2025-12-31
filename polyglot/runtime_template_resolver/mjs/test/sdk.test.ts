/**
 * Unit tests for SDK functions.
 *
 * Tests cover:
 * - Statement coverage for all SDK functions
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 */
import { describe, it, expect } from '@jest/globals';
import { SDK } from '../src/sdk.js';
import { validatePlaceholder } from '../src/validator.js';
import { extractPlaceholders } from '../src/extractor.js';
import { ValidationError } from '../src/errors.js';

const sampleContext = {
    name: 'World',
    user: {
        profile: {
            name: 'Alice',
            age: 30
        }
    },
    count: 42,
    items: ['apple', 'banana', 'cherry']
};

describe('SDK', () => {
    describe('resolve()', () => {
        it('should resolve simple template', () => {
            const result = SDK.resolve('Hello {{name}}!', sampleContext);
            expect(result).toBe('Hello World!');
        });

        it('should resolve nested path', () => {
            const result = SDK.resolve('User: {{user.profile.name}}', sampleContext);
            expect(result).toBe('User: Alice');
        });

        it('should resolve with default value', () => {
            const result = SDK.resolve('Value: {{missing | "default"}}', {});
            expect(result).toBe('Value: default');
        });
    });

    describe('resolveMany()', () => {
        it('should resolve multiple templates', () => {
            const templates = [
                'Hello {{name}}!',
                'User: {{user.profile.name}}',
                'Count: {{count}}'
            ];
            const results = SDK.resolveMany(templates, sampleContext);
            expect(results).toEqual([
                'Hello World!',
                'User: Alice',
                'Count: 42'
            ]);
        });

        it('should handle empty array', () => {
            const results = SDK.resolveMany([], sampleContext);
            expect(results).toEqual([]);
        });

        it('should handle single item', () => {
            const results = SDK.resolveMany(['Hello {{name}}'], sampleContext);
            expect(results).toEqual(['Hello World']);
        });
    });

    describe('resolveObject()', () => {
        it('should resolve templates in dict', () => {
            const obj = { greeting: 'Hello {{name}}!' };
            const result = SDK.resolveObject(obj, sampleContext) as any;
            expect(result.greeting).toBe('Hello World!');
        });

        it('should resolve templates in array', () => {
            const obj = ['Hello {{name}}', 'Count: {{count}}'];
            const result = SDK.resolveObject(obj, sampleContext) as any;
            expect(result).toEqual(['Hello World', 'Count: 42']);
        });

        it('should resolve nested structures', () => {
            const obj = {
                level1: {
                    level2: {
                        value: '{{name}}'
                    }
                }
            };
            const result = SDK.resolveObject(obj, sampleContext) as any;
            expect(result.level1.level2.value).toBe('World');
        });

        it('should pass through non-string values', () => {
            const obj = { number: 42, boolean: true };
            const result = SDK.resolveObject(obj, sampleContext) as any;
            expect(result.number).toBe(42);
            expect(result.boolean).toBe(true);
        });
    });

    describe('validate()', () => {
        it('should validate valid template', () => {
            expect(() => SDK.validate('Hello {{name}}!')).not.toThrow();
        });

        it('should validate nested path', () => {
            expect(() => SDK.validate('{{user.profile.name}}')).not.toThrow();
        });

        it('should validate template with default', () => {
            expect(() => SDK.validate('{{missing | "default"}}')).not.toThrow();
        });

        it('should validate array access', () => {
            expect(() => SDK.validate('{{items[0]}}')).not.toThrow();
        });

        it('should not throw for empty placeholder (not matched by regex)', () => {
            // {{}} does not match the regex, so validate() finds no placeholders
            expect(() => SDK.validate('{{}}')).not.toThrow();
        });

        it('should throw for invalid characters', () => {
            expect(() => SDK.validate('{{foo@bar}}')).toThrow(ValidationError);
        });

        it('should throw for double dots', () => {
            expect(() => SDK.validate('{{foo..bar}}')).toThrow(ValidationError);
        });
    });

    describe('extract()', () => {
        it('should extract single placeholder', () => {
            const result = SDK.extract('Hello {{name}}!');
            expect(result).toEqual(['name']);
        });

        it('should extract multiple placeholders', () => {
            const result = SDK.extract('{{a}} and {{b}} and {{c}}');
            expect(result).toEqual(['a', 'b', 'c']);
        });

        it('should return empty for no placeholders', () => {
            const result = SDK.extract('No placeholders here');
            expect(result).toEqual([]);
        });

        it('should extract nested paths', () => {
            const result = SDK.extract('{{user.profile.name}}');
            expect(result).toEqual(['user.profile.name']);
        });

        it('should extract placeholders with defaults', () => {
            const result = SDK.extract('{{missing | "default"}}');
            expect(result).toEqual(['missing | "default"']);
        });
    });

    describe('compile()', () => {
        it('should return callable function', () => {
            const compiled = SDK.compile('Hello {{name}}!');
            expect(typeof compiled).toBe('function');
        });

        it('should resolve template when called', () => {
            const compiled = SDK.compile('Hello {{name}}!');
            const result = compiled({ name: 'World' });
            expect(result).toBe('Hello World!');
        });

        it('should be reusable', () => {
            const compiled = SDK.compile('Count: {{count}}');
            expect(compiled({ count: 1 })).toBe('Count: 1');
            expect(compiled({ count: 2 })).toBe('Count: 2');
            expect(compiled({ count: 3 })).toBe('Count: 3');
        });
    });
});

describe('validatePlaceholder()', () => {
    it('should pass for valid simple key', () => {
        expect(() => validatePlaceholder('name')).not.toThrow();
    });

    it('should pass for valid nested key', () => {
        expect(() => validatePlaceholder('user.profile.name')).not.toThrow();
    });

    it('should pass for valid array index', () => {
        expect(() => validatePlaceholder('items[0]')).not.toThrow();
    });

    it('should throw for empty string', () => {
        expect(() => validatePlaceholder('')).toThrow(ValidationError);
    });

    it('should throw for whitespace only', () => {
        expect(() => validatePlaceholder('   ')).toThrow(ValidationError);
    });

    it('should throw for invalid characters', () => {
        expect(() => validatePlaceholder('foo@bar')).toThrow(ValidationError);
    });
});

describe('extractPlaceholders()', () => {
    it('should extract basic placeholder', () => {
        const result = extractPlaceholders('{{name}}');
        expect(result).toEqual(['name']);
    });

    it('should extract and strip spaces', () => {
        const result = extractPlaceholders('{{  name  }}');
        expect(result).toEqual(['name']);
    });

    it('should return empty for no placeholders', () => {
        const result = extractPlaceholders('no placeholders');
        expect(result).toEqual([]);
    });
});
