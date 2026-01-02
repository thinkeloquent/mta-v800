import { randomUUID } from 'crypto';

let createRegistry, ComputeScope, contextResolverPlugin;
let HAS_RESOLVER = false;

try {
    const resolver = await import('runtime-template-resolver');
    createRegistry = resolver.createRegistry;
    ComputeScope = resolver.ComputeScope;
    const integrations = await import('runtime-template-resolver/integrations/fastify');
    contextResolverPlugin = integrations.contextResolverPlugin;
    HAS_RESOLVER = true;
} catch (e) {
    console.warn('runtime-template-resolver not available:', e.message);
}

function registerComputeFunctions(registry) {
    // ==========================================================================
    // STARTUP Scope - Run once at startup, cached
    // ==========================================================================

    // Echo for testing
    registry.register("echo", () => "echo", ComputeScope.STARTUP);

    // Build info from environment
    registry.register("get_build_id", (ctx) => ctx?.env?.BUILD_ID || "dev-local", ComputeScope.STARTUP);
    registry.register("get_build_version", (ctx) => ctx?.env?.BUILD_VERSION || "0.0.0", ComputeScope.STARTUP);
    registry.register("get_git_commit", (ctx) => ctx?.env?.GIT_COMMIT || "unknown", ComputeScope.STARTUP);

    // Service info
    registry.register("get_service_name", (ctx) => ctx?.config?.app?.name || "mta-server", ComputeScope.STARTUP);
    registry.register("get_service_version", (ctx) => ctx?.config?.app?.version || "0.0.0", ComputeScope.STARTUP);

    // ==========================================================================
    // REQUEST Scope - Run per request with request context
    // ==========================================================================

    // Request ID - from header or generate
    registry.register("compute_request_id", (ctx) => {
        const request = ctx?.request;
        if (request) {
            const requestId = request.headers["x-request-id"];
            if (requestId) return requestId;
        }
        return randomUUID();
    }, ComputeScope.REQUEST);

    // Gemini token - from header or env
    registry.register("compute_localhost_test_case_001_token", (ctx) => {
        const request = ctx?.request;
        if (request) {
            const token = request.headers["x-gemini-token"];
            if (token) return token;
        }
        return ctx?.env?.GEMINI_API_KEY || "";
    }, ComputeScope.REQUEST);

    // Test case 002 - Authorization from jira provider
    registry.register("test_case_002", (ctx) => {
        const request = ctx?.request;
        if (request) {
            const token = request.headers["x-jira-token"];
            if (token) return `Bearer ${token}`;
        }
        const apiToken = ctx?.env?.JIRA_API_TOKEN;
        if (apiToken) return `Bearer ${apiToken}`;
        return "";
    }, ComputeScope.REQUEST);

    // Test case 002_1 - X-Auth header
    registry.register("test_case_002_1", (ctx) => {
        const request = ctx?.request;
        if (request) {
            const token = request.headers["x-auth"];
            if (token) return token;
        }
        return ctx?.env?.JIRA_API_TOKEN || "";
    }, ComputeScope.REQUEST);

    // Tenant ID - from header or query param
    registry.register("compute_tenant_id", (ctx) => {
        const request = ctx?.request;
        if (request) {
            const tenantIdHeader = request.headers["x-tenant-id"];
            if (tenantIdHeader) return tenantIdHeader;
            const tenantIdQuery = request.query?.tenant_id;
            if (tenantIdQuery) return tenantIdQuery;
        }
        return "default";
    }, ComputeScope.REQUEST);

    // User agent with app info
    registry.register("compute_user_agent", (ctx) => {
        const appName = ctx?.config?.app?.name || "MTA-Server";
        const appVersion = ctx?.config?.app?.version || "0.0.0";
        const baseUA = `${appName}/${appVersion}`;
        const request = ctx?.request;
        if (request) {
            const clientUA = request.headers["user-agent"];
            if (clientUA) return `${baseUA} (via ${clientUA})`;
        }
        return baseUA;
    }, ComputeScope.REQUEST);
}

export async function onStartup(server, config) {
    if (!HAS_RESOLVER) {
        server.log.warn("runtime-template-resolver not installed. Context resolver skipping.");
        return;
    }

    server.log.info("Initializing Runtime Template Resolver...");

    // server.config is AppYamlConfig instance (decorated in 01)
    const appConfig = server.config;
    if (!appConfig) {
        server.log.warn("server.config not found. Context resolver skipping.");
        return;
    }

    // Get raw config
    const rawConfig = appConfig.toObject ? appConfig.toObject() : (appConfig.getAll ? appConfig.getAll() : {});

    const registry = createRegistry(server.log);
    registerComputeFunctions(registry);

    // Register plugin which handles decoration and STARTUP resolution
    await server.register(contextResolverPlugin, {
        config: rawConfig,
        registry: registry,
        instanceProperty: 'resolvedConfig',
        requestProperty: 'resolvedConfig',
        logger: server.log
    });

    // Decorate server with registry for healthz access
    if (!server.hasDecorator('contextRegistry')) {
        server.decorate('contextRegistry', registry);
    }
    if (!server.hasDecorator('contextRawConfig')) {
        server.decorate('contextRawConfig', rawConfig);
    }

    server.log.info(`Runtime Template Resolver initialized. Registered functions: ${registry.list()}`);
}
