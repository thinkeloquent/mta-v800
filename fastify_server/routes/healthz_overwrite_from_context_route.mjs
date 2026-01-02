/**
 * Mount overwrite-from-context health check routes to the Fastify application.
 * This function is called by the server bootstrap process.
 * @param {import('fastify').FastifyInstance} server
 */
export async function mount(server) {
  server.get("/healthz/admin/overwrite-from-context/status", async (request, reply) => {
    try {
      const registry = server.contextRegistry;
      if (!registry) {
        return {
          initialized: false,
          error: "Context resolver not configured",
        };
      }
      return {
        initialized: true,
        registeredFunctions: registry.list(),
      };
    } catch (e) {
      return {
        initialized: false,
        error: e.message,
      };
    }
  });

  server.get("/healthz/admin/overwrite-from-context/json", async (request, reply) => {
    try {
      const registry = server.contextRegistry;
      const rawConfig = server.contextRawConfig;
      const resolvedConfig = server.resolvedConfig;

      if (!registry) {
        return {
          initialized: false,
          error: "Context resolver not configured",
        };
      }

      const functionNames = registry.list();
      const functionScopes = {};
      for (const name of functionNames) {
        functionScopes[name] = registry.getScope(name);
      }
      return {
        initialized: true,
        config: {
          registeredFunctions: functionNames,
          functionScopes,
          rawConfig,
          resolvedConfig,
        },
      };
    } catch (e) {
      return {
        initialized: false,
        error: e.message,
      };
    }
  });

  server.get("/healthz/admin/overwrite-from-context/keys", async (request, reply) => {
    try {
      const registry = server.contextRegistry;

      if (!registry) {
        return {
          initialized: false,
          error: "Context resolver not configured",
        };
      }

      return {
        initialized: true,
        registeredFunctions: registry.list(),
      };
    } catch (e) {
      return {
        initialized: false,
        error: e.message,
      };
    }
  });

  server.get("/healthz/admin/overwrite-from-context/overwrite", async (request, reply) => {
    try {
      const registry = server.contextRegistry;
      const rawConfig = server.contextRawConfig;

      if (!registry) {
        return {
          initialized: false,
          error: "Context resolver not configured",
        };
      }

      // Import resolver and scope
      let createResolver, ComputeScope;
      try {
        const mod = await import("runtime-template-resolver");
        createResolver = mod.createResolver;
        ComputeScope = mod.ComputeScope;
      } catch (e) {
        return {
          initialized: false,
          error: "runtime-template-resolver not installed",
        };
      }

      // Get app config from server.config (AppYamlConfig instance)
      const serverConfig = server.config;
      const appConfigDict = serverConfig?.getAll?.() || serverConfig?.toObject?.() || rawConfig || {};

      // Build REQUEST context
      const requestContext = {
        env: process.env,
        config: rawConfig,
        app: appConfigDict?.app || {},
        state: request.state || {},
        request: request,
      };

      // Resolve with REQUEST scope
      const resolver = createResolver(registry);
      const resolvedWithRequest = await resolver.resolveObject(
        rawConfig,
        requestContext,
        ComputeScope.REQUEST
      );

      return {
        initialized: true,
        overwriteResolved: resolvedWithRequest,
      };
    } catch (e) {
      return {
        initialized: false,
        error: e.message,
      };
    }
  });
}
