
import fp from 'fastify-plugin';
import { FastifyInstance, FastifyRequest, FastifyPluginAsync } from 'fastify';
import { createResolver, createRegistry } from '../sdk.js';
import { ComputeScope } from '../options.js';
import { Logger } from '../logger.js';
import _ from 'lodash';
const { set } = _;

export interface ContextResolverPluginOptions {
    config: Record<string, any>;
    registry?: any; // ComputeRegistry type
    instanceProperty?: string;
    requestProperty?: string;
    logger?: Logger;
}

// Declare module augmentation for Fastify
declare module 'fastify' {
    interface FastifyInstance {
        [key: string]: any;
    }
    interface FastifyRequest {
        [key: string]: any;
    }
}

const contextResolverPluginCallback: FastifyPluginAsync<ContextResolverPluginOptions> = async (fastify, options) => {
    const logger = options.logger || Logger.create('runtime-template-resolver', 'integrations/fastify.ts');
    const registry = options.registry || createRegistry(logger);
    const resolver = createResolver(registry, { logger }, logger);
    const rawConfig = options.config;

    const instanceProp = options.instanceProperty || 'config';
    const requestProp = options.requestProperty || 'config';

    // STARTUP Resolution
    logger.debug('Resolving configuration (STARTUP scope)...');

    // Get app config from server.config (AppYamlConfig instance decorated by 01-app-yaml)
    const serverConfig = (fastify as any).config;
    const appConfig = serverConfig?.getAll?.() || serverConfig?.toObject?.() || rawConfig || {};

    // Expose app at top level for {{app.name}} etc.
    const startupContext = {
        env: process.env,
        config: rawConfig,
        app: appConfig?.app || {}
    };

    const resolvedStartupConfig = await resolver.resolveObject(
        rawConfig,
        startupContext,
        ComputeScope.STARTUP
    );

    // Decorate Instance
    // Handle dot notation? Fastify decorate support dot notation? No.
    // Lodash set? But we need to decorate the instance.
    // Usually decoration is flat property.
    // If instanceProperty has dots, e.g. "state.config", we assume "state" exists or we set it on instance?
    // Fastify decorate logic is strict.
    // "decorate fastify instance with config" -> simple decorate if no dots.

    if (instanceProp.includes('.')) {
        // Use lodash set on fastify instance (might bypass decorate checks but works on obj)
        set(fastify, instanceProp, resolvedStartupConfig);
    } else {
        if (!fastify.hasDecorator(instanceProp)) {
            fastify.decorate(instanceProp, resolvedStartupConfig);
        } else {
            // Overwrite?
            (fastify as any)[instanceProp] = resolvedStartupConfig;
        }
    }

    // REQUEST Resolution Hook
    fastify.addHook('onRequest', async (request: FastifyRequest) => {
        // Get app config from server.config (AppYamlConfig instance)
        const srvConfig = (fastify as any).config;
        const appCfg = srvConfig?.getAll?.() || srvConfig?.toObject?.() || rawConfig || {};

        // Expose app at top level for {{app.name}} etc., and state for request.state
        const reqContext = {
            env: process.env,
            config: rawConfig,
            app: appCfg?.app || {},
            state: (request as any).state || {},
            request: request
        };

        const resolvedRequestConfig = await resolver.resolveObject(
            rawConfig,
            reqContext,
            ComputeScope.REQUEST
        );

        if (requestProp.includes('.')) {
            set(request, requestProp, resolvedRequestConfig);
        } else {
            (request as any)[requestProp] = resolvedRequestConfig;
            // We can't use decorateRequest here because we are in a hook, request already created?
            // Actually `fastify.decorateRequest(prop, null)` at startup is good practice.
            // But valid dynamic assignment is fine.
        }
    });

    // Decorate request helper only if needed?
    // Plan: "Decorate request.resolveContext() helper"
    fastify.decorateRequest('resolveContext', async function (this: FastifyRequest, expr: any) {
        // Get app config from server.config (AppYamlConfig instance)
        const srvCfg = (fastify as any).config;
        const appCfg2 = srvCfg?.getAll?.() || srvCfg?.toObject?.() || rawConfig || {};

        // Expose app at top level for {{app.name}} etc., and state for request.state
        const reqContext = {
            env: process.env,
            config: rawConfig,
            app: appCfg2?.app || {},
            state: (this as any).state || {},
            request: this
        };
        return resolver.resolve(expr, reqContext, ComputeScope.REQUEST);
    });

    logger.debug('Context Resolver plugin registered');
}

export const contextResolverPlugin = fp(contextResolverPluginCallback, {
    name: 'runtime-template-resolver'
});
