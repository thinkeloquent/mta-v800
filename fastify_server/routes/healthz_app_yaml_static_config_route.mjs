import { AppYamlConfig, AppYamlConfigSDK } from "app-yaml-static-config";

/**
 * Mount app-yaml-static-config health check routes to the Fastify application.
 * This function is called by the server bootstrap process.
 * @param {import('fastify').FastifyInstance} server
 */
export async function mount(server) {
  server.get("/healthz/admin/app-yaml-static-config/status", async (request, reply) => {
    try {
      const instance = AppYamlConfig.getInstance();
      const sdk = new AppYamlConfigSDK(instance);
      return {
        initialized: true,
        providers: sdk.listProviders(),
        services: sdk.listServices(),
        storages: sdk.listStorages(),
      };
    } catch (e) {
      return {
        initialized: false,
        error: e.message,
      };
    }
  });

  server.get("/healthz/admin/app-yaml-static-config/json", async (request, reply) => {
    try {
      const instance = AppYamlConfig.getInstance();
      const sdk = new AppYamlConfigSDK(instance);
      const originalMap = instance.getOriginalAll();
      const originalFiles = Object.fromEntries(originalMap);
      return {
        initialized: true,
        config: sdk.getAll(),
        originalFiles,
      };
    } catch (e) {
      return {
        initialized: false,
        error: e.message,
      };
    }
  });

  server.get("/healthz/admin/app-yaml-static-config/keys", async (request, reply) => {
    try {
      const instance = AppYamlConfig.getInstance();
      const config = instance.getAll();
      const originalMap = instance.getOriginalAll();
      return {
        initialized: true,
        topLevelKeys: Object.keys(config),
        loadedFiles: Array.from(originalMap.keys()),
      };
    } catch (e) {
      return {
        initialized: false,
        error: e.message,
      };
    }
  });
}
