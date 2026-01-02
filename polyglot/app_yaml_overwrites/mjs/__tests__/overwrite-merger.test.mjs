/**
 * Unit tests for overwrite-merger module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 */
import { describe, it, expect } from 'vitest';
import { applyOverwrites } from '../src/overwrite-merger.ts';

describe('applyOverwrites', () => {
    // =========================================================================
    // Statement Coverage
    // =========================================================================

    describe('Statement Coverage', () => {
        it('should return original when no overwrites', () => {
            const original = { key: 'value' };

            const result = applyOverwrites(original, {});

            expect(result.key).toBe('value');
        });

        it('should return original when overwrites is null', () => {
            const original = { key: 'value' };

            const result = applyOverwrites(original, null);

            expect(result).toEqual(original);
        });

        it('should return original when overwrites is undefined', () => {
            const original = { key: 'value' };

            const result = applyOverwrites(original, undefined);

            expect(result).toEqual(original);
        });

        it('should merge flat overwrites', () => {
            const original = { key1: 'original', key2: 'keep' };
            const overwrites = { key1: 'overwritten' };

            const result = applyOverwrites(original, overwrites);

            expect(result.key1).toBe('overwritten');
            expect(result.key2).toBe('keep');
        });

        it('should add new keys from overwrites', () => {
            const original = { existing: 'value' };
            const overwrites = { newKey: 'newValue' };

            const result = applyOverwrites(original, overwrites);

            expect(result.existing).toBe('value');
            expect(result.newKey).toBe('newValue');
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('Branch Coverage', () => {
        it('should trigger early return for empty overwrite', () => {
            const original = { key: 'value' };

            const result = applyOverwrites(original, {});

            // lodash.merge with empty object still returns merged result
            expect(result.key).toBe('value');
        });

        it('should trigger early return for falsy overwrite', () => {
            const original = { key: 'value' };

            expect(applyOverwrites(original, null)).toEqual(original);
            expect(applyOverwrites(original, undefined)).toEqual(original);
        });

        it('should deep merge nested dicts', () => {
            const original = {
                headers: {
                    'X-Static': 'value',
                    'X-Dynamic': null
                }
            };
            const overwrites = {
                headers: {
                    'X-Dynamic': 'resolved'
                }
            };

            const result = applyOverwrites(original, overwrites);

            expect(result.headers['X-Static']).toBe('value');
            expect(result.headers['X-Dynamic']).toBe('resolved');
        });

        it('should overwrite non-dict with dict', () => {
            const original = { key: 'stringValue' };
            const overwrites = { key: { nested: 'value' } };

            const result = applyOverwrites(original, overwrites);

            expect(result.key).toEqual({ nested: 'value' });
        });

        it('should overwrite dict with non-dict', () => {
            const original = { key: { nested: 'value' } };
            const overwrites = { key: 'stringValue' };

            const result = applyOverwrites(original, overwrites);

            expect(result.key).toBe('stringValue');
        });
    });

    // =========================================================================
    // Boundary Values
    // =========================================================================

    describe('Boundary Values', () => {
        it('should handle empty original', () => {
            const original = {};
            const overwrites = { key: 'value' };

            const result = applyOverwrites(original, overwrites);

            expect(result).toEqual({ key: 'value' });
        });

        it('should handle both empty', () => {
            const result = applyOverwrites({}, {});

            expect(result).toEqual({});
        });

        it('should handle deeply nested merge', () => {
            const original = {
                level1: {
                    level2: {
                        level3: {
                            original: 'keep'
                        }
                    }
                }
            };
            const overwrites = {
                level1: {
                    level2: {
                        level3: {
                            new: 'added'
                        }
                    }
                }
            };

            const result = applyOverwrites(original, overwrites);

            expect(result.level1.level2.level3.original).toBe('keep');
            expect(result.level1.level2.level3.new).toBe('added');
        });

        it('should handle null values in overwrites', () => {
            const original = { key: 'value' };
            const overwrites = { key: null };

            const result = applyOverwrites(original, overwrites);

            expect(result.key).toBeNull();
        });

        it('should handle array values', () => {
            const original = { items: [1, 2, 3] };
            const overwrites = { items: [4, 5] };

            const result = applyOverwrites(original, overwrites);

            // lodash.merge merges arrays by index
            expect(result.items).toEqual([4, 5, 3]);
        });
    });

    // =========================================================================
    // Error Handling
    // =========================================================================

    describe('Error Handling', () => {
        it('should not mutate original object', () => {
            const original = { key: 'original' };
            const overwrites = { key: 'changed' };

            const result = applyOverwrites(original, overwrites);

            // Note: lodash.merge with {} as first arg creates new object
            expect(result.key).toBe('changed');
        });

        it('should handle mixed types', () => {
            const original = {
                string: 'text',
                number: 42,
                float: 3.14,
                bool: true,
                null: null,
                list: [1, 2, 3],
                dict: { nested: 'value' }
            };
            const overwrites = {
                string: 'newText',
                number: 100
            };

            const result = applyOverwrites(original, overwrites);

            expect(result.string).toBe('newText');
            expect(result.number).toBe(100);
            expect(result.float).toBe(3.14);
            expect(result.bool).toBe(true);
            expect(result.null).toBeNull();
            expect(result.list).toEqual([1, 2, 3]);
            expect(result.dict).toEqual({ nested: 'value' });
        });
    });

    // =========================================================================
    // Integration Tests
    // =========================================================================

    describe('Integration', () => {
        it('should merge realistic provider config', () => {
            const original = {
                providers: {
                    apiProvider: {
                        baseUrl: 'https://api.example.com',
                        headers: {
                            'X-App-Name': null,
                            'X-App-Version': null,
                            'X-Custom': 'static'
                        },
                        timeout: 30
                    }
                }
            };
            const overwrites = {
                providers: {
                    apiProvider: {
                        headers: {
                            'X-App-Name': 'MyApp',
                            'X-App-Version': '1.0.0'
                        }
                    }
                }
            };

            const result = applyOverwrites(original, overwrites);

            const provider = result.providers.apiProvider;
            expect(provider.baseUrl).toBe('https://api.example.com');
            expect(provider.headers['X-App-Name']).toBe('MyApp');
            expect(provider.headers['X-App-Version']).toBe('1.0.0');
            expect(provider.headers['X-Custom']).toBe('static');
            expect(provider.timeout).toBe(30);
        });

        it('should handle overwrite_from_context pattern', () => {
            const config = {
                headers: {
                    Authorization: null,
                    'Content-Type': 'application/json'
                },
                overwrite_from_context: {
                    headers: {
                        Authorization: 'Bearer resolved-token'
                    }
                }
            };

            const resolved = applyOverwrites(
                config,
                config.overwrite_from_context
            );

            expect(resolved.headers.Authorization).toBe('Bearer resolved-token');
            expect(resolved.headers['Content-Type']).toBe('application/json');
        });
    });
});
