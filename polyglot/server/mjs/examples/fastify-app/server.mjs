/**
 * Fastify Example Application
 *
 * A minimal Fastify server demonstrating integration with the server package.
 * This example shows:
 * - Server initialization with configuration
 * - Request state management via decorators and hooks
 * - Health and feature-specific demo routes
 * - Server decoration patterns
 *
 * Run: node server.mjs
 */

import path from "path";
import { fileURLToPath } from "url";
import { randomUUID } from "crypto";

// Import from parent src directory
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const srcPath = path.join(__dirname, "..", "..", "src");

// Dynamic imports
const logger = (await import(path.join(srcPath, "logger.mjs"))).default;
const { init, start, stop } = await import(path.join(srcPath, "server.mjs"));

// =============================================================================
// Configuration
// =============================================================================

// Mock configuration (in production, load from app-yaml or environment)
const CONFIG = {
    title: "Fastify Example Server",
    version: "1.0.0",
    host: process.env.HOST || "0.0.0.0",
    port: parseInt(process.env.PORT || "8080", 10),
    logger: false, // Disable Fastify's built-in logger, use our own

    // Initial request state (cloned per request)
    initial_state: {
        user: null,
        authenticated: false,
        permissions: [],
        requestId: null,
    },
};

// Create logger for this module
const log = logger.create("fastify_app", import.meta.url);


// =============================================================================
// Type Augmentation (for TypeScript users - documented in JSDoc)
// =============================================================================

/**
 * @typedef {Object} RequestState
 * @property {string|null} user - Current user
 * @property {boolean} authenticated - Whether user is authenticated
 * @property {string[]} permissions - User permissions
 * @property {string|null} requestId - Unique request ID
 */


// =============================================================================
// Application Factory
// =============================================================================

/**
 * Create and configure the Fastify application.
 * @returns {import('fastify').FastifyInstance} Configured Fastify instance
 */
function createApp() {
    // Initialize server with configuration
    const server = init(CONFIG);

    // ==========================================================================
    // Server Decorations
    // ==========================================================================

    // Decorate server with configuration
    server.decorate("config", CONFIG);

    // Decorate server with version
    server.decorate("version", CONFIG.version);

    // ==========================================================================
    // Request Decorations
    // ==========================================================================

    // Decorate request with state (will be set per-request)
    server.decorateRequest("state", null);

    // Decorate request with requestId helper
    server.decorateRequest("requestId", null);

    // ==========================================================================
    // Hooks
    // ==========================================================================

    // Initialize request state on each request
    server.addHook("onRequest", async (request, reply) => {
        // Deep clone initial state
        const state = structuredClone(CONFIG.initial_state);

        // Generate unique request ID
        state.requestId = randomUUID().substring(0, 8);

        // Set request state
        request.state = state;
        request.requestId = state.requestId;

        log.trace("Request initialized", {
            requestId: state.requestId,
            method: request.method,
            url: request.url,
        });
    });

    // Log request completion
    server.addHook("onResponse", async (request, reply) => {
        log.trace("Request completed", {
            requestId: request.requestId,
            statusCode: reply.statusCode,
            responseTime: reply.elapsedTime,
        });
    });

    // ==========================================================================
    // Routes
    // ==========================================================================

    // Root endpoint
    server.get("/", async (request, reply) => {
        return { message: "Welcome to Fastify Example Server" };
    });

    // Health check endpoint
    server.get("/health", {
        schema: {
            response: {
                200: {
                    type: "object",
                    properties: {
                        status: { type: "string" },
                        service: { type: "string" },
                        version: { type: "string" },
                    },
                },
            },
        },
    }, async (request, reply) => {
        log.debug("Health check requested");
        return {
            status: "ok",
            service: server.config.title,
            version: server.version,
        };
    });

    // Echo endpoint
    server.get("/echo/:message", async (request, reply) => {
        const { message } = request.params;
        const { user } = request.state;

        log.info("Echo requested", { message, user });

        return {
            message,
            user,
        };
    });

    // Current user endpoint
    server.get("/me", async (request, reply) => {
        const { user, authenticated, permissions } = request.state;

        return {
            user,
            authenticated,
            permissions,
        };
    });

    // Request state endpoint
    server.get("/state", async (request, reply) => {
        const { requestId, user, authenticated } = request.state;

        return {
            requestId,
            user,
            authenticated,
        };
    });

    // Simulated login endpoint
    server.post("/login", async (request, reply) => {
        const username = request.body?.username || "demo_user";

        // Modify state for THIS request only
        request.state.user = username;
        request.state.authenticated = true;
        request.state.permissions = ["read", "write"];

        log.info("User logged in (for this request)", { user: username });

        return {
            message: `Logged in as ${username}`,
            note: "State is per-request; next request starts fresh",
        };
    });

    // Configuration endpoint
    server.get("/config", async (request, reply) => {
        return {
            title: server.config.title,
            version: server.version,
        };
    });

    // Debug route tree
    server.get("/routes", async (request, reply) => {
        return {
            routes: server.printRoutes({ commonPrefix: false }),
        };
    });

    return server;
}


// =============================================================================
// Main Entry Point
// =============================================================================

async function main() {
    log.info("Creating Fastify application");
    const server = createApp();

    // Handle graceful shutdown
    const signals = ["SIGINT", "SIGTERM"];
    for (const signal of signals) {
        process.on(signal, async () => {
            log.info(`Received ${signal}, shutting down...`);
            await stop(server, CONFIG);
            process.exit(0);
        });
    }

    try {
        log.info("Starting server", {
            host: CONFIG.host,
            port: CONFIG.port,
        });

        // Start the server (this will listen and block)
        await start(server, CONFIG);

    } catch (err) {
        log.error("Server failed to start", {}, err);
        process.exit(1);
    }
}

// Run main
main().catch((err) => {
    console.error("Fatal error:", err);
    process.exit(1);
});
