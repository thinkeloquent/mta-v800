import fp from 'fastify-plugin';
import { AppYamlConfig, AppYamlConfigSDK } from 'app-yaml-static-config';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// This file matches the signature bound by `server.mjs`:
// if (module.onStartup) startupHooks.push(module.onStartup);

export async function onStartup(server, config) {
    console.log("Initializing App Yaml Static Config...");

    // In this context, 'server' is the Fastify instance

    // We can assume config is accessible or derived
    const configDir = process.env.CONFIG_DIR || path.join(__dirname, '..', '..', '..', 'common', 'config');

    server.log.debug({ configDir }, "Initializing Configuration");

    // We register it as a plugin to ensure decorations happen in correct scope if needed,
    // although this hook is called just before listen().

    // Since we are inside an async startup hook, we can just await the initialization
    const appEnv = (process.env.APP_ENV || 'dev').toLowerCase();  // Normalize to lowercase
    await AppYamlConfig.initialize({
        files: [
            path.join(configDir, 'base.yml'),
            path.join(configDir, `server.${appEnv}.yaml`)
        ],
        configDir
    });

    const appConfig = AppYamlConfig.getInstance();
    const sdk = new AppYamlConfigSDK(appConfig);

    server.log.info({ providers: sdk.listProviders() }, 'Configuration loaded');

    // Decorate Fastify instance for global access
    // Note: server.config may already be decorated with bootstrap config by server.mjs
    // We overwrite it with AppYamlConfig instance which has getAll()/toObject() methods
    if (!server.hasDecorator('config')) {
        server.decorate('config', appConfig);
    } else {
        // Overwrite existing bootstrap config with AppYamlConfig
        server.config = appConfig;
    }
    if (!server.hasDecorator('sdk')) {
        server.decorate('sdk', sdk);
    }
}
