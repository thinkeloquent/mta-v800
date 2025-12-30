import Fastify from "fastify";
import closeWithGrace from "close-with-grace";
import path from "path";
import fs from "fs";
import { glob } from "glob";
import logger from "./logger.mjs";

const log = logger.create("server", import.meta.url);

// --- Interface Implementation ---

export function init(config) {
    /** Initialize and return native Fastify instance. */
    log.debug("Initializing Fastify server", { title: config.title });
    const server = Fastify({
        logger: config.logger ?? true,
    });
    log.info("Fastify server initialized", { title: config.title });
    return server;
}

export async function start(server, config) {
    /** Start server with bootstrap configuration. */
    log.info("Starting server bootstrap sequence", { title: config.title });
    const bootstrap = config.bootstrap || {};
    const startupHooks = [];
    const shutdownHooks = [];

    // Bootstrap: glob and execute env loader modules from directory
    if (bootstrap.load_env) {
        log.debug("Loading environment modules", { path: bootstrap.load_env });
        if (fs.existsSync(bootstrap.load_env)) {
            const moduleFiles = glob.sync(path.join(bootstrap.load_env, "*.mjs")).sort();
            log.trace("Found env modules", { count: moduleFiles.length, files: moduleFiles });
            for (const modulePath of moduleFiles) {
                // Resolve absolute path for import
                const absolutePath = path.resolve(modulePath);
                log.debug("Loading env module", { module: absolutePath });
                await import(absolutePath);  // Module loads its own .env files
            }
            log.info("Environment modules loaded", { count: moduleFiles.length });
        } else {
            log.warn("Environment directory does not exist", { path: bootstrap.load_env });
        }
    }

    // Bootstrap: glob and load lifecycle modules from directory
    if (bootstrap.lifecycle) {
        log.debug("Loading lifecycle modules", { path: bootstrap.lifecycle });
        if (fs.existsSync(bootstrap.lifecycle)) {
            const moduleFiles = glob.sync(path.join(bootstrap.lifecycle, "*.mjs")).sort();
            log.trace("Found lifecycle modules", { count: moduleFiles.length, files: moduleFiles });
            for (const modulePath of moduleFiles) {
                const absolutePath = path.resolve(modulePath);
                log.debug("Loading lifecycle module", { module: absolutePath });
                const module = await import(absolutePath);
                if (module.onStartup) startupHooks.push(module.onStartup);
                if (module.onShutdown) shutdownHooks.push(module.onShutdown);
            }
            log.info("Lifecycle modules loaded", { count: moduleFiles.length, startupHooks: startupHooks.length, shutdownHooks: shutdownHooks.length });
        } else {
            log.warn("Lifecycle directory does not exist", { path: bootstrap.lifecycle });
        }
    }

    // Run startup hooks with (server, config) BEFORE server.listen()
    log.debug("Executing startup hooks", { count: startupHooks.length });
    for (const hook of startupHooks) {
        log.trace("Running startup hook", { hookName: hook.name || "anonymous" });
        await hook(server, config);
    }
    log.info("Startup hooks completed", { count: startupHooks.length });

    // Store for shutdown
    // Using decorate safely (checking if exists first or just overwriting if we own it)
    if (!server.hasDecorator("_shutdownHooks")) {
        server.decorate("_shutdownHooks", shutdownHooks);
    } else {
        server._shutdownHooks = shutdownHooks;
    }

    if (!server.hasDecorator("_config")) {
        server.decorate("_config", config);
    } else {
        server._config = config;
    }

    // Feature: Initial Request State
    // If config provides 'initial_state', deep clone it to request.state for every request
    if (config.initial_state) {
        log.debug("Configuring initial request state", { keys: Object.keys(config.initial_state) });
        // Decorate server with the template state
        if (!server.hasDecorator("initialState")) {
            server.decorate("initialState", config.initial_state);
        }

        // Define the 'state' property on the request object
        if (!server.hasRequestDecorator("state")) {
            server.decorateRequest("state", null);
        }

        // Add hook to deep clone state on every request
        server.addHook("onRequest", async (request, reply) => {
            // Using structuredClone for deep copy (Node.js 17+)
            request.state = structuredClone(server.initialState);
            log.trace("Request state initialized", { requestId: request.id });
        });
        log.info("Initial request state feature enabled");
    }


    // Register shutdown hooks to run on close
    if (shutdownHooks.length > 0) {
        log.debug("Registering shutdown hooks", { count: shutdownHooks.length });
        server.addHook("onClose", async () => {
            log.info("Executing shutdown hooks", { count: shutdownHooks.length });
            for (const hook of shutdownHooks) {
                log.trace("Running shutdown hook", { hookName: hook.name || "anonymous" });
                await hook(server, config);
            }
            log.info("Shutdown hooks completed");
        });
    }

    // Handle OS signals (SIGTERM, SIGINT) with delayed exit via close-with-grace
    log.debug("Registering graceful shutdown handlers", { delay: 30000 });
    const closeListeners = closeWithGrace({ delay: 30000 }, async ({ signal, err, manual }) => {
        if (err) {
            log.error("Error during shutdown", err);
            server.log.error(err);
        }
        log.info("Graceful shutdown initiated", { signal, manual });
        server.log.info(`Received ${signal}, shutting down gracefully...`);
        await server.close();
        log.info("Server closed successfully");
    });

    // Attach the listeners to the server close event to remove them if server closes manually
    server.addHook('onClose', async () => {
        log.debug("Uninstalling close listeners");
        closeListeners.uninstall();
    })

    const host = config.host || "0.0.0.0";
    const port = parseInt(process.env.PORT || config.port || 8080, 10);
    log.info("Starting HTTP listener", { host, port });
    await server.listen({ host, port });
    log.info("Server listening", { host, port, address: server.addresses() });
}

export async function stop(server, config) {
    /** Gracefully stop the server. */
    log.info("Stop requested", { title: config?.title });
    await server.close();
    log.info("Server stopped");
}
