import { EnvStore } from "vault-file";

/**
 * Mount vault-file health check routes to the Fastify application.
 * This function is called by the server bootstrap process.
 * @param {import('fastify').FastifyInstance} server
 */
export async function mount(server) {
  server.get("/healthz/admin/vault-file/status", async (request, reply) => {
    const instance = EnvStore.getInstance();
    return {
      initialized: EnvStore.isInitialized(),
      totalVarsLoaded: instance["_totalVarsLoaded"] || 0,
    };
  });

  server.get("/healthz/admin/vault-file/json", async (request, reply) => {
    const instance = EnvStore.getInstance();
    const store = instance["store"] || {};
    return {
      initialized: EnvStore.isInitialized(),
      totalVarsLoaded: instance["_totalVarsLoaded"] || 0,
      store: { ...store },
    };
  });

  server.get("/healthz/admin/vault-file/keys", async (request, reply) => {
    const instance = EnvStore.getInstance();
    const store = instance["store"] || {};
    return {
      initialized: EnvStore.isInitialized(),
      totalVarsLoaded: instance["_totalVarsLoaded"] || 0,
      keys: Object.keys(store),
    };
  });
}
