import { Logger } from './logger.js';
import { ResolverOptions } from './options.js';
import { ComputeRegistry } from './compute-registry.js';
import { ContextResolver } from './context-resolver.js';

export function createRegistry(logger?: Logger): ComputeRegistry {
    return new ComputeRegistry(logger);
}

export function createResolver(
    registry?: ComputeRegistry,
    options?: ResolverOptions,
    logger?: Logger
): ContextResolver {
    const reg = registry || createRegistry(logger);

    if (logger && !options) {
        options = { logger };
    } else if (logger && options && !options.logger) {
        options.logger = logger;
    }

    return new ContextResolver(reg, options);
}
