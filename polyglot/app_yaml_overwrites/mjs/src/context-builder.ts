import { FastifyRequest } from 'fastify';

export interface ContextOptions {
    env?: Record<string, string>;
    config?: any; // AppYamlConfig raw
    app?: any;    // Extracted app config
    state?: any;
    request?: FastifyRequest;
}

export type ContextExtender = (currentContext: any, request?: FastifyRequest) => Promise<any> | any;

export class ContextBuilder {
    static async build(options: ContextOptions, extenders: ContextExtender[] = []): Promise<any> {
        const baseContext = {
            env: options.env || process.env,
            config: options.config || {},
            app: options.app || {},
            state: options.state || {},
            request: options.request, // Only present if request scope
        };

        let context = { ...baseContext };

        for (const extender of extenders) {
            const partial = await extender(context, options.request);
            context = { ...context, ...partial };
        }

        return context;
    }
}
