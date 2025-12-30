import Fastify from 'fastify';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import { EnvStore, VaultFileSDK } from '../../src/index.js';

// Setup demo env file
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DEMO_ENV_FILE = path.join(__dirname, '.env.demo');
if (!fs.existsSync(DEMO_ENV_FILE)) {
    fs.writeFileSync(DEMO_ENV_FILE, 'SERVER_PORT=3000\\nAPI_KEY=secret_123');
}

const fastify = Fastify({ logger: true });

// --- Server Lifecycle with EnvStore ---

/**
 * Initialize EnvStore before server start.
 * This ensures all config is loaded and validated.
 */
async function bootstrap() {
    // initialize EnvStore
    const sdk = VaultFileSDK.create()
        .withEnvPath(DEMO_ENV_FILE)
        .build();

    await sdk.loadConfig();
}

// --- Routes ---

fastify.get('/health', async () => {
    return { status: 'ok', initialized: EnvStore.isInitialized() };
});

fastify.get('/config-demo', async () => {
    // Demonstration of accessing config
    return {
        port_configured: EnvStore.get('SERVER_PORT'),
        api_key_masked: EnvStore.get('API_KEY') ? '***' : 'missing'
    };
});

// --- Start ---

const start = async () => {
    try {
        await bootstrap();

        const port = parseInt(EnvStore.get('SERVER_PORT') || '3000');
        await fastify.listen({ port, host: '0.0.0.0' });

    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

// Handle cleanup
process.on('SIGINT', () => {
    if (fs.existsSync(DEMO_ENV_FILE)) {
        fs.unlinkSync(DEMO_ENV_FILE);
    }
    process.exit(0);
});

start();
