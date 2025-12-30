import Fastify from "fastify";
import closeWithGrace from "close-with-grace";
import path from "path";
import fs from "fs";
import { glob } from "glob";

// --- Interface Implementation ---

export function init(config) {
    /** Initialize and return native Fastify instance. */
    const server = Fastify({
        logger: config.logger ?? true,
    });
    return server;
}

export async function start(server, config) {
    /** Start server with bootstrap configuration. */
    const bootstrap = config.bootstrap || {};
    const startupHooks = [];
    const shutdownHooks = [];

    // Bootstrap: glob and execute env loader modules from directory
    if (bootstrap.load_env) {
        if (fs.existsSync(bootstrap.load_env)) {
            const moduleFiles = glob.sync(path.join(bootstrap.load_env, "*.mjs")).sort();
            for (const modulePath of moduleFiles) {
                // Resolve absolute path for import
                const absolutePath = path.resolve(modulePath);
                await import(absolutePath);  // Module loads its own .env files
            }
        }
    }

    // Bootstrap: glob and load lifecycle modules from directory
    if (bootstrap.lifecycle) {
        if (fs.existsSync(bootstrap.lifecycle)) {
            const moduleFiles = glob.sync(path.join(bootstrap.lifecycle, "*.mjs")).sort();
            for (const modulePath of moduleFiles) {
                const absolutePath = path.resolve(modulePath);
                const module = await import(absolutePath);
                if (module.onStartup) startupHooks.push(module.onStartup);
                if (module.onShutdown) shutdownHooks.push(module.onShutdown);
            }
        }
    }

    // Run startup hooks with (server, config) BEFORE server.listen()
    for (const hook of startupHooks) {
        await hook(server, config);
    }

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
        });
    }


    // Register shutdown hooks to run on close
    if (shutdownHooks.length > 0) {
        server.addHook("onClose", async () => {
            for (const hook of shutdownHooks) {
                await hook(server, config);
            }
        });
    }

    // Handle OS signals (SIGTERM, SIGINT) with delayed exit via close-with-grace
    const closeListeners = closeWithGrace({ delay: 30000 }, async ({ signal, err, manual }) => {
        if (err) {
            server.log.error(err);
        }
        server.log.info(`Received ${signal}, shutting down gracefully...`);
        await server.close();
    });

    // Attach the listeners to the server close event to remove them if server closes manually
    server.addHook('onClose', async () => {
        closeListeners.uninstall();
    })

    await server.listen({
        host: config.host || "0.0.0.0",
        port: parseInt(process.env.PORT || config.port || 8080, 10),
    });
}

export async function stop(server, config) {
    /** Gracefully stop the server. */
    await server.close();
}
