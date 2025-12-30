import fp from 'fastify-plugin';
import { AppYamlConfig, AppYamlConfigSDK } from 'app-yaml-static-config';
import * as path from 'path';

// This file matches the signature bound by `server.mjs`:
// if (module.onStartup) startupHooks.push(module.onStartup);

export async function onStartup(server, config) {
    console.log("Initializing App Yaml Static Config...");

    // In this context, 'server' is the Fastify instance

    // We can assume config is accessible or derived
    const configDir = process.env.CONFIG_DIR || path.join(process.cwd(), '..', 'common', 'config');

    server.log.debug({ configDir }, "Initializing Configuration");

    // We register it as a plugin to ensure decorations happen in correct scope if needed,
    // although this hook is called just before listen().

    // Since we are inside an async startup hook, we can just await the initialization
    await AppYamlConfig.initialize({
        files: [
            path.join(configDir, 'base.yml'),
            path.join(configDir, `server.${process.env.APP_ENV || 'dev'}.yaml`)
        ],
        configDir
    });

    const appConfig = AppYamlConfig.getInstance();
    const sdk = new AppYamlConfigSDK(appConfig);

    server.log.info({ providers: sdk.listProviders() }, 'Configuration loaded');

    // Decorate Fastify instance for global access
    if (!server.hasDecorator('config')) {
        server.decorate('config', appConfig);
    }
    if (!server.hasDecorator('sdk')) {
        server.decorate('sdk', sdk);
    }
}
