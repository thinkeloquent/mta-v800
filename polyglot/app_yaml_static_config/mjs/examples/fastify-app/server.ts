/**
 * Fastify Integration Example
 *
 * Demonstrates how to integrate AppYamlConfig into a Fastify server using decorators.
 */

import Fastify from 'fastify';
import fp from 'fastify-plugin';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { AppYamlConfig } from '../../src/index.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, '..', '..', '__fixtures__');

// =============================================================================
// 1. Define Plugin for Config Injection
// =============================================================================

// Perform module augmentation to type the decoration
declare module 'fastify' {
    interface FastifyInstance {
        config: AppYamlConfig;
    }
}

const configPlugin = fp(async (fastify, opts) => {
    // Initialize config (simulated for this example using fixtures)
    // In a real app, you might look for config/app.yaml relative to process.cwd()
    const configFile = path.join(FIXTURES_DIR, 'base.yaml');

    console.log(`Loading config from: ${configFile}`);

    await AppYamlConfig.initialize({
        files: [configFile],
        configDir: FIXTURES_DIR,
    });

    const configInstance = AppYamlConfig.getInstance();

    // Decorate the Fastify instance
    fastify.decorate('config', configInstance);
});

// =============================================================================
// 2. Server Setup
// =============================================================================

async function runServer() {
    const server = Fastify({ logger: true });

    // Register configuration plugin
    await server.register(configPlugin);

    // =========================================================================
    // 3. Define Routes
    // =========================================================================

    server.get('/health', async (request, reply) => {
        return { status: 'ok' };
    });

    server.get('/demo/config', async (request, reply) => {
        // Access config via the decorator
        const appName = server.config.getNested(['app', 'name']);
        const environment = server.config.getNested(['app', 'environment'], 'unknown');

        return {
            message: 'Configuration accessed successfully via decorator',
            appName,
            environment
        };
    });

    try {
        const port = 3000;
        await server.listen({ port });
        console.log(`\n🚀 Server running at http://localhost:${port}`);
        console.log(`   Try: curl http://localhost:${port}/demo/config\n`);
    } catch (err) {
        server.log.error(err);
        process.exit(1);
    }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
    runServer();
}
