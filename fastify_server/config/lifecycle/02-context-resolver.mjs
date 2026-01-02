
import { createRegistry, ComputeScope } from 'runtime-template-resolver';
import { contextResolverPlugin } from 'runtime-template-resolver/integrations/fastify'; // Import from subpath if exports allowed, or main index?
// Node exports might separate integrations.
// If index.ts doesn't export integrations, we need deep import.
// My mjs/package.json exports?
// I haven't configured package.json exports map. 
// So imports usually work if file exists.
// But typescript compilation output structure? `dist/src/integrations/fastify.js`?
// I need to be careful with imports.
// Check generated structure. Usually `runtime-template-resolver` main points to index.js.
// If I exported `integrations` in `index.ts` (I didn't), I could import from main.
// I should export integrations from index.ts or use deep import.
// Let's assume deep import matches file structure in `dist`.

function registerComputeFunctions(registry) {
    registry.register("echo", () => "echo", ComputeScope.STARTUP);
}

export async function onStartup(server, config) {
    server.log.info("Initializing Runtime Template Resolver...");

    // server.config is AppYamlConfig instance (decorated in 01).
    const appConfig = server.config;
    if (!appConfig) {
        server.log.warn("server.config not found. Context resolver skipping.");
        return;
    }

    // Get raw config
    const rawConfig = appConfig.toObject ? appConfig.toObject() : (appConfig.config || {});

    const registry = createRegistry(server.log); // reuse server logger?
    registerComputeFunctions(registry);

    // Register plugin which handles decoration and STARTUP resolution
    await server.register(contextResolverPlugin, {
        config: rawConfig,
        registry: registry,
        instanceProperty: 'resolvedConfig',
        requestProperty: 'resolvedConfig',
        logger: server.log
    });

    server.log.info("Runtime Template Resolver initialized. Resolved config available at server.resolvedConfig");
}
