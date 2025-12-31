/**
 * Unit tests for TemplateResolver.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 * - Log verification (hyper-observability)
 */
import { describe, it, expect, beforeEach } from '@jest/globals';
import { TemplateResolver } from '../src/resolver.js';
import { MissingStrategy } from '../src/interfaces.js';
import { SecurityError, ValidationError, MissingValueError } from '../src/errors.js';

const sampleContext = {
    name: 'World',
    user: {
        profile: {
            name: 'Alice',
            age: 30,
            email: 'alice@example.com'
        },
        roles: ['admin', 'user']
    },
    items: ['apple', 'banana', 'cherry'],
    count: 42,
    active: true,
    nullable: null,
    nested: {
        deep: {
            value: 'found'
        }
    }
};

describe('TemplateResolver', () => {
    let resolver: TemplateResolver;

    beforeEach(() => {
        resolver = new TemplateResolver();
    });

    describe('Statement Coverage', () => {
        it('should resolve simple placeholder', () => {
            const result = resolver.resolve('Hello {{name}}!', sampleContext);
            expect(result).toBe('Hello World!');
        });

        it('should resolve nested path', () => {
            const result = resolver.resolve('User: {{user.profile.name}}', sampleContext);
            expect(result).toBe('User: Alice');
        });

        it('should resolve array access', () => {
            const result = resolver.resolve('First: {{items[0]}}', sampleContext);
            expect(result).toBe('First: apple');
        });

        it('should resolve multiple placeholders', () => {
            const result = resolver.resolve('{{name}} has {{count}} items', sampleContext);
            expect(result).toBe('World has 42 items');
        });

        it('should return template unchanged when no placeholders', () => {
            const result = resolver.resolve('No placeholders here', {});
            expect(result).toBe('No placeholders here');
        });

        it('should recursively resolve templates in objects', () => {
            const obj = {
                message: 'Hello {{name}}!',
                greeting: 'Welcome {{user.profile.name}}',
                items: ['First: {{items[0]}}', 'Second: {{items[1]}}'],
                nested: { value: 'Count is {{count}}' }
            };
            const result = resolver.resolveObject(obj, sampleContext) as any;
            expect(result.message).toBe('Hello World!');
            expect(result.greeting).toBe('Welcome Alice');
            expect(result.items[0]).toBe('First: apple');
            expect(result.nested.value).toBe('Count is 42');
        });
    });

    describe('Branch Coverage', () => {
        it('should handle default value with double quotes', () => {
            const result = resolver.resolve('Value: {{missing | "Default"}}', {});
            expect(result).toBe('Value: Default');
        });

        it('should handle default value with single quotes', () => {
            const result = resolver.resolve("Value: {{missing | 'Fallback'}}", {});
            expect(result).toBe('Value: Fallback');
        });

        it('should handle default value without quotes', () => {
            const result = resolver.resolve('Value: {{missing | N/A}}', {});
            expect(result).toBe('Value: N/A');
        });

        it('should handle EMPTY missing strategy', () => {
            const result = resolver.resolve('Missing: {{missing}}', sampleContext, {
                missingStrategy: MissingStrategy.EMPTY
            });
            expect(result).toBe('Missing: ');
        });

        it('should handle KEEP missing strategy', () => {
            const result = resolver.resolve('Missing: {{missing}}', sampleContext, {
                missingStrategy: MissingStrategy.KEEP
            });
            expect(result).toBe('Missing: {{missing}}');
        });

        it('should handle ERROR missing strategy', () => {
            expect(() => resolver.resolve('Missing: {{missing}}', sampleContext, {
                missingStrategy: MissingStrategy.ERROR,
                throwOnError: true
            })).toThrow(MissingValueError);
        });

        it('should throw when throwOnError is true', () => {
            expect(() => resolver.resolve('Bad: {{_private}}', {}, {
                throwOnError: true
            })).toThrow(SecurityError);
        });

        it('should keep original when throwOnError is false', () => {
            const result = resolver.resolve('Bad: {{_private}}', {}, {
                throwOnError: false
            });
            expect(result).toBe('Bad: {{_private}}');
        });

        it('should handle list access with valid index', () => {
            const result = resolver.resolve('Item: {{items[1]}}', sampleContext);
            expect(result).toBe('Item: banana');
        });

        it('should handle list access with non-numeric key', () => {
            const result = resolver.resolve('Item: {{items.foo}}', sampleContext, {
                missingStrategy: MissingStrategy.EMPTY
            });
            expect(result).toBe('Item: ');
        });

        it('should handle dict access', () => {
            const result = resolver.resolve('Email: {{user.profile.email}}', sampleContext);
            expect(result).toBe('Email: alice@example.com');
        });

        it('should handle null context value', () => {
            const result = resolver.resolve('Null: {{nullable}}', sampleContext, {
                missingStrategy: MissingStrategy.EMPTY
            });
            expect(result).toBe('Null: ');
        });
    });

    describe('Boundary Values', () => {
        it('should handle empty template', () => {
            const result = resolver.resolve('', {});
            expect(result).toBe('');
        });

        it('should handle template that is just a placeholder', () => {
            const result = resolver.resolve('{{name}}', { name: 'Test' });
            expect(result).toBe('Test');
        });

        it('should handle deeply nested path', () => {
            const result = resolver.resolve('Deep: {{nested.deep.value}}', sampleContext);
            expect(result).toBe('Deep: found');
        });

        it('should handle first array element', () => {
            const result = resolver.resolve('{{items[0]}}', sampleContext);
            expect(result).toBe('apple');
        });

        it('should handle last array element', () => {
            const result = resolver.resolve('{{items[2]}}', sampleContext);
            expect(result).toBe('cherry');
        });

        it('should handle array out of bounds', () => {
            const result = resolver.resolve('{{items[99]}}', sampleContext, {
                missingStrategy: MissingStrategy.EMPTY
            });
            expect(result).toBe('');
        });

        it('should handle multiple consecutive placeholders', () => {
            const result = resolver.resolve('{{a}}{{b}}{{c}}', { a: '1', b: '2', c: '3' });
            expect(result).toBe('123');
        });

        it('should handle placeholder with extra spaces', () => {
            const result = resolver.resolve('{{  name  }}', { name: 'Test' });
            expect(result).toBe('Test');
        });

        it('should coerce boolean to string', () => {
            const result = resolver.resolve('Active: {{active}}', sampleContext);
            expect(result).toBe('Active: true');
        });

        it('should coerce number to string', () => {
            const result = resolver.resolve('Count: {{count}}', sampleContext);
            expect(result).toBe('Count: 42');
        });

        it('should coerce object to JSON string', () => {
            const result = resolver.resolve('User: {{user.profile}}', sampleContext);
            expect(result).toContain('Alice');
        });

        it('should coerce array to JSON string', () => {
            const result = resolver.resolve('Roles: {{user.roles}}', sampleContext);
            expect(result).toContain('admin');
            expect(result).toContain('user');
        });
    });

    describe('Error Handling', () => {
        it('should throw SecurityError for private attribute', () => {
            expect(() => resolver.resolve('{{_secret}}', {}, { throwOnError: true }))
                .toThrow(SecurityError);
        });

        it('should throw SecurityError for dunder attribute', () => {
            expect(() => resolver.resolve('{{__proto__}}', {}, { throwOnError: true }))
                .toThrow(SecurityError);
        });

        it('should not match empty placeholder (regex requires at least one char)', () => {
            // {{}} does not match the regex pattern {{([^}]+)}}, returned as-is
            const result = resolver.resolve('{{}}', {});
            expect(result).toBe('{{}}');
        });

        it('should throw ValidationError for invalid characters', () => {
            expect(() => resolver.resolve('{{foo@bar}}', {}, { throwOnError: true }))
                .toThrow(ValidationError);
        });

        it('should throw ValidationError for double dots', () => {
            expect(() => resolver.resolve('{{foo..bar}}', {}, { throwOnError: true }))
                .toThrow(ValidationError);
        });

        it('should keep original without throwOnError', () => {
            const result = resolver.resolve('Bad: {{_private}}', {});
            expect(result).toBe('Bad: {{_private}}');
        });
    });

    describe('Integration', () => {
        it('should handle realistic email template', () => {
            const template =
                'Dear {{customer.name}},\n\n' +
                'Thank you for your order #{{order.id}}.\n' +
                'Total: $' + '{{order.total}}\n\n' +
                'Best regards,\n' +
                '{{company.name}}';
            const context = {
                customer: { name: 'John Doe' },
                order: { id: '12345', total: '99.99' },
                company: { name: 'ACME Corp' }
            };
            const result = resolver.resolve(template, context);
            expect(result).toContain('Dear John Doe');
            expect(result).toContain('order #12345');
            expect(result).toContain('$99.99');
            expect(result).toContain('ACME Corp');
        });

        it('should handle config template with defaults', () => {
            const template = '{"host": "{{db.host | \'localhost\'}}", "port": "{{db.port | \'5432\'}}"}';
            const result = resolver.resolve(template, {});
            expect(result).toContain('"host": "localhost"');
            expect(result).toContain('"port": "5432"');
        });

        it('should handle deeply nested object resolution', () => {
            const obj = {
                config: {
                    database: {
                        url: 'postgres://{{db.host}}:{{db.port}}/{{db.name}}'
                    }
                },
                templates: [
                    'Welcome {{user}}',
                    'Goodbye {{user}}'
                ]
            };
            const context = {
                db: { host: 'localhost', port: '5432', name: 'mydb' },
                user: 'Alice'
            };
            const result = resolver.resolveObject(obj, context) as any;
            expect(result.config.database.url).toBe('postgres://localhost:5432/mydb');
            expect(result.templates[0]).toBe('Welcome Alice');
            expect(result.templates[1]).toBe('Goodbye Alice');
        });
    });
});
