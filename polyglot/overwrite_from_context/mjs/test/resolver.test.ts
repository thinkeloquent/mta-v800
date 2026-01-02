import { describe, it, expect, beforeAll } from 'vitest';
import * as path from 'path';
import * as fs from 'fs';
import { createResolver, createRegistry } from '../src/sdk.js';
import { ComputeScope } from '../src/options.js';
import { ResolveError } from '../src/errors.js';

const FIXTURES_PATH = path.join(__dirname, '../../__fixtures__/test_vectors.json');
const vectors = JSON.parse(fs.readFileSync(FIXTURES_PATH, 'utf-8')).vectors;

describe('Runtime Template Resolver Parity Tests', () => {

    it.each(vectors)('$name', async (vector) => {
        const registry = createRegistry();

        if (vector.setup) {
            const { fn: fnName, returns: retVal } = vector.setup;
            registry.register(fnName, async () => retVal, ComputeScope.REQUEST);
        }

        const resolver = createResolver(registry);
        const context = vector.context;
        const expression = vector.expression;
        const depth = vector.depth || 0; // Handled by resolve call param but our resolve API exposes it?
        // resolve(express, context, scope, depth)
        // Ensure resolver supports passing depth if needed for test, 
        // OR wrapper.

        if (vector.expected_error) {
            await expect(resolver.resolve(expression, context, ComputeScope.REQUEST, depth))
                .rejects.toThrowError();

            // Check code (requires custom matcher or try/catch)
            try {
                await resolver.resolve(expression, context, ComputeScope.REQUEST, depth);
            } catch (e: any) {
                expect(e.code).toBe(vector.expected_error);
            }
        } else {
            const result = await resolver.resolve(expression, context, ComputeScope.REQUEST, depth);
            expect(result).toBe(vector.expected_resolve);
        }
    });

});
