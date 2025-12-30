#!/usr/bin/env node
/**
 * Basic Usage Examples for Server Package
 *
 * This script demonstrates the core features of the server package:
 * - Logger utility with multiple log levels
 * - Server initialization and configuration
 * - Request state management
 * - Lifecycle hooks
 *
 * Run: node basic-usage.mjs
 */

import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import os from "os";

// Import from parent src directory
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const srcPath = path.join(__dirname, "..", "src");

// Dynamic import to handle path resolution
const logger = (await import(path.join(srcPath, "logger.mjs"))).default;
const { init } = await import(path.join(srcPath, "server.mjs"));


// =============================================================================
// Example 1: Basic Logger Usage
// =============================================================================
/**
 * Demonstrates basic logger creation and usage.
 * The logger provides a Console-like interface with log levels.
 */
function example1_basic_logging() {
    console.log("\n" + "=".repeat(60));
    console.log("Example 1: Basic Logger Usage");
    console.log("=".repeat(60));

    // Create a logger for this module
    const log = logger.create("examples", import.meta.url);

    // Log at different levels
    log.info("This is an info message");
    log.debug("This is a debug message (may not show at default level)");
    log.warn("This is a warning message");

    // Log with additional data
    log.info("Request received", { method: "GET", path: "/api/users" });

    // Log with error context
    try {
        throw new Error("Something went wrong");
    } catch (e) {
        log.error("Operation failed", { operation: "example" }, e);
    }

    console.log("Logger example completed.\n");
}


// =============================================================================
// Example 2: Logger Configuration
// =============================================================================
/**
 * Demonstrates logger configuration options.
 * You can customize log level, colors, timestamps, and output format.
 */
function example2_logger_configuration() {
    console.log("\n" + "=".repeat(60));
    console.log("Example 2: Logger Configuration");
    console.log("=".repeat(60));

    // Custom log level - only show debug and above
    const logDebug = logger.create("examples", import.meta.url, { level: "debug" });
    logDebug.debug("This debug message will show");
    logDebug.trace("This trace message will NOT show (below debug level)");

    // JSON format output
    const logJson = logger.create("examples", import.meta.url, { json: true });
    logJson.info("This message is in JSON format", { format: "json" });

    // Disable colors
    const logNoColor = logger.create("examples", import.meta.url, { colorize: false });
    logNoColor.info("This message has no ANSI colors");

    // Custom output function
    const capturedLogs = [];
    const logCustom = logger.create("examples", import.meta.url, {
        output: {
            log: (msg) => capturedLogs.push(msg),
            error: (msg) => capturedLogs.push(msg),
        },
    });
    logCustom.info("This message is captured");
    console.log(`Captured log: ${capturedLogs[0].substring(0, 50)}...`);

    console.log("Logger configuration example completed.\n");
}


// =============================================================================
// Example 3: Child and Context Loggers
// =============================================================================
/**
 * Demonstrates child loggers and context loggers.
 * Useful for maintaining package context while varying module/context.
 */
function example3_child_context_loggers() {
    console.log("\n" + "=".repeat(60));
    console.log("Example 3: Child and Context Loggers");
    console.log("=".repeat(60));

    // Create parent logger
    const log = logger.create("myapp", import.meta.url);

    // Create child logger for a sub-module
    const childLog = log.child("submodule.mjs");
    childLog.info("Message from child logger (different filename)");

    // Create context logger with persistent context data
    const requestLog = log.withContext({ requestId: "abc-123", user: "admin" });
    requestLog.info("Processing request");
    requestLog.info("Request completed", { durationMs: 45 });

    console.log("Child and context logger example completed.\n");
}


// =============================================================================
// Example 4: Server Initialization
// =============================================================================
/**
 * Demonstrates server initialization with configuration.
 * The init() function returns a Fastify instance.
 */
async function example4_server_initialization() {
    console.log("\n" + "=".repeat(60));
    console.log("Example 4: Server Initialization");
    console.log("=".repeat(60));

    // Basic server initialization
    const config = {
        title: "My API Server",
        host: "127.0.0.1",
        port: 8080,
        logger: false, // Disable Fastify's built-in logger for this example
    };

    const server = init(config);
    console.log(`Server initialized: ${config.title}`);

    // Add a simple route
    server.get("/", async () => ({ message: "Hello, World!" }));
    server.get("/health", async () => ({ status: "ok" }));

    // Ready the server (required before listing routes)
    await server.ready();

    console.log("Routes registered:", server.printRoutes());
    console.log("Server initialization example completed.\n");

    await server.close();
}


// =============================================================================
// Example 5: Initial Request State
// =============================================================================
/**
 * Demonstrates the initial_state feature.
 * State is deep-cloned for each request, ensuring isolation.
 */
function example5_initial_request_state() {
    console.log("\n" + "=".repeat(60));
    console.log("Example 5: Initial Request State");
    console.log("=".repeat(60));

    // Server with initial state
    const config = {
        title: "Stateful API",
        logger: false,
        initial_state: {
            user: null,
            permissions: [],
            requestMetadata: {
                version: "1.0",
                environment: "development",
            },
        },
    };

    const server = init(config);
    console.log(`Server initialized with initial_state keys: ${Object.keys(config.initial_state)}`);

    // The middleware will deep-clone this state for each request
    // This means mutations in one request won't affect others
    console.log("Each request gets a fresh deep copy of initial_state");
    console.log("Initial request state example completed.\n");
}


// =============================================================================
// Example 6: Lifecycle Hooks
// =============================================================================
/**
 * Demonstrates lifecycle hooks (onStartup/onShutdown).
 * Hooks are loaded from modules in the lifecycle directory.
 */
async function example6_lifecycle_hooks() {
    console.log("\n" + "=".repeat(60));
    console.log("Example 6: Lifecycle Hooks");
    console.log("=".repeat(60));

    // Create a temporary lifecycle directory with a hook module
    const tmpdir = fs.mkdtempSync(path.join(os.tmpdir(), "lifecycle-"));

    try {
        // Create a lifecycle hook module
        const lifecycleFile = path.join(tmpdir, "example_hooks.mjs");
        fs.writeFileSync(lifecycleFile, `
export function onStartup(server, config) {
    console.log("  [Hook] Server starting:", config.title);
    // You can decorate the server, setup connections, etc.
    server.decorate("startupTime", new Date());
}

export async function onShutdown(server, config) {
    console.log("  [Hook] Server stopping:", config.title);
    // Clean up resources, close connections, etc.
}
`);

        console.log(`Created lifecycle hook at: ${lifecycleFile}`);
        console.log("Hooks will be executed by start() function:");
        console.log("  - onStartup: runs before server.listen()");
        console.log("  - onShutdown: runs on server.close()");

    } finally {
        // Clean up
        fs.rmSync(tmpdir, { recursive: true, force: true });
    }

    console.log("Lifecycle hooks example completed.\n");
}


// =============================================================================
// Example 7: Environment Loading
// =============================================================================
/**
 * Demonstrates loading environment modules from a directory.
 * Useful for loading .env files or setting up environment variables.
 */
async function example7_environment_loading() {
    console.log("\n" + "=".repeat(60));
    console.log("Example 7: Environment Loading");
    console.log("=".repeat(60));

    // Create a temporary env directory with a loader module
    const tmpdir = fs.mkdtempSync(path.join(os.tmpdir(), "env-"));

    try {
        // Create an env loader module
        const envFile = path.join(tmpdir, "load_env.mjs");
        fs.writeFileSync(envFile, `
// Set environment variables for the application
if (!process.env.API_KEY) {
    process.env.API_KEY = "development-key";
}
if (!process.env.DATABASE_URL) {
    process.env.DATABASE_URL = "sqlite:///dev.db";
}

console.log("  [Env] Environment variables loaded");
`);

        console.log(`Created env loader at: ${envFile}`);
        console.log("Env modules are executed during start() before lifecycle hooks");

    } finally {
        // Clean up
        fs.rmSync(tmpdir, { recursive: true, force: true });
    }

    console.log("Environment loading example completed.\n");
}


// =============================================================================
// Example 8: Full Server Configuration
// =============================================================================
/**
 * Demonstrates a complete server configuration combining all features.
 * This is a realistic example of production-like configuration.
 */
async function example8_full_configuration() {
    console.log("\n" + "=".repeat(60));
    console.log("Example 8: Full Server Configuration");
    console.log("=".repeat(60));

    const config = {
        // Basic server settings
        title: "Production API",
        host: "0.0.0.0",
        port: 8080,
        logger: false,

        // Initial request state (cloned per request)
        initial_state: {
            user: null,
            authenticated: false,
            permissions: [],
            traceId: null,
        },

        // Bootstrap configuration
        bootstrap: {
            // load_env: "./env",      // Load .env modules
            // lifecycle: "./hooks",    // Load lifecycle hooks
        },
    };

    const server = init(config);

    // Add routes
    server.get("/api/v1/status", async () => ({
        service: config.title,
        status: "healthy",
        version: "1.0.0",
    }));

    console.log("Full configuration example:");
    console.log(`  Title: ${config.title}`);
    console.log(`  Host: ${config.host}:${config.port}`);
    console.log(`  Initial state keys: ${Object.keys(config.initial_state)}`);
    console.log("Full configuration example completed.\n");
}


// =============================================================================
// Main Runner
// =============================================================================
/**
 * Run all examples sequentially.
 */
async function main() {
    console.log("\n" + "=".repeat(60));
    console.log("Server Package - Basic Usage Examples");
    console.log("=".repeat(60));

    // Set log level to debug for examples
    process.env.LOG_LEVEL = "debug";

    const examples = [
        example1_basic_logging,
        example2_logger_configuration,
        example3_child_context_loggers,
        example4_server_initialization,
        example5_initial_request_state,
        example6_lifecycle_hooks,
        example7_environment_loading,
        example8_full_configuration,
    ];

    for (const exampleFn of examples) {
        try {
            await exampleFn();
        } catch (e) {
            console.log(`Example failed: ${e.message}`);
        }
    }

    console.log("\n" + "=".repeat(60));
    console.log("All examples completed!");
    console.log("=".repeat(60));
}

// Run main
main().catch(console.error);
