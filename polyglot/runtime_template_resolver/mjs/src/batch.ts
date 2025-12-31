import { ITemplateResolver, IResolverOptions } from './interfaces.js';

export function resolveObject(obj: unknown, context: Record<string, unknown>, resolver: ITemplateResolver, options?: IResolverOptions, depth = 0): unknown {
    if (depth > 10) return obj; // Max depth

    if (typeof obj === 'string') {
        return resolver.resolve(obj, context, options);
    }

    if (Array.isArray(obj)) {
        return obj.map(item => resolveObject(item, context, resolver, options, depth + 1));
    }

    if (typeof obj === 'object' && obj !== null) {
        const result: Record<string, unknown> = {};
        for (const [key, value] of Object.entries(obj)) {
            result[key] = resolveObject(value, context, resolver, options, depth + 1);
        }
        return result;
    }

    return obj;
}
