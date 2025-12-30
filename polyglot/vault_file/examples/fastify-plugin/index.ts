import fp from 'fastify-plugin';
import { EnvStore } from '@internal/vault-file';

/**
 * Fastify plugin for Vault File integration
 */
export default fp(async (fastify, opts) => {
    try {
        const result = await EnvStore.onStartup();
        fastify.log.info({
            plugin: 'fastify-vault-file',
            totalVars: result.totalVarsLoaded
        }, 'Environment variables loaded via Vault File');
    } catch (err) {
        fastify.log.error(err, 'Failed to load Vault File environment');
        throw err;
    }
});
