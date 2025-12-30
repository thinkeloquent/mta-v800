import fs from "fs";
import path from "path";
import { globSync } from "glob";
import logger from "./logger.mjs";

const log = logger.create("autoload_routes", import.meta.url);

/**
 * Autoload route modules from the configured directory.
 * Modules must export a 'mount(server)' function.
 * 
 * @param {import("fastify").FastifyInstance} server 
 * @param {Object} bootstrap 
 */
export async function autoloadRoutes(server, bootstrap) {
    if (bootstrap.routes) {
        log.debug("Loading route modules", { path: bootstrap.routes });
        if (fs.existsSync(bootstrap.routes)) {
            const moduleFiles = globSync(path.join(bootstrap.routes, "*.mjs")).sort();
            log.trace("Found route modules", { count: moduleFiles.length, files: moduleFiles });
            for (const modulePath of moduleFiles) {
                const absolutePath = path.resolve(modulePath);
                log.debug("Loading route module", { module: absolutePath });
                try {
                    const module = await import(absolutePath);
                    if (typeof module.mount === "function") {
                        log.trace("Mounting route module", { module: path.basename(modulePath) });
                        await module.mount(server);
                    } else {
                        log.warn("Route module does not export 'mount' function", { module: absolutePath });
                    }
                } catch (err) {
                    log.error("Failed to load route module", { module: absolutePath, error: err.message });
                }
            }
            log.info("Route modules loaded", { count: moduleFiles.length });
        } else {
            log.warn("Routes directory does not exist", { path: bootstrap.routes });
        }
    }
}
