import fp from 'fastify-plugin';
import { FastifyInstance, FastifyPluginAsync } from 'fastify';
import { IResolverOptions } from '../interfaces.js';
import { TemplateResolver } from '../resolver.js';
import { logger } from '../logger.js';

// Need to augment fastify type
declare module 'fastify' {
    interface FastifyRequest {
        resolveTemplate(template: string, context: Record<string, unknown>, options?: IResolverOptions): string;
    }
}

export interface FastifyTemplateResolverOptions extends IResolverOptions {
    // plugin specific options if any
}

const fastifyTemplateResolver: FastifyPluginAsync<FastifyTemplateResolverOptions> = async (fastify, opts) => {
    const resolver = new TemplateResolver();
    const log = logger.create('runtime-template-resolver/fastify', 'plugin');

    fastify.decorateRequest('resolveTemplate', function (this: any, template: string, context: Record<string, unknown>, options?: IResolverOptions) {
        const reqLog = this.log || log;

        // Wrap fastify logger to match our LoggerInterface
        const wrappedLogger = {
            debug: (msg: string, ctx?: any) => reqLog.debug({ ...ctx, msg }),
            info: (msg: string, ctx?: any) => reqLog.info({ ...ctx, msg }),
            warn: (msg: string, ctx?: any) => reqLog.warn({ ...ctx, msg }),
            error: (msg: string, ctx?: any) => reqLog.error({ ...ctx, msg }),
        };

        const mergedOptions = { ...opts, ...options, logger: wrappedLogger };
        return resolver.resolve(template, context, mergedOptions);
    });
};

export default fp(fastifyTemplateResolver, {
    name: '@internal/runtime-template-resolver',
    fastify: '4.x'
});
