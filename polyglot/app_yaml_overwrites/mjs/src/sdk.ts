import { AppYamlConfig } from 'app-yaml-static-config';
import { createResolver, ComputeScope } from 'runtime-template-resolver';
import { Logger } from './logger.js';
import { ContextBuilder, ContextExtender } from './context-builder.js';
import { applyOverwrites } from './overwrite-merger.js';
import { FastifyRequest } from 'fastify';

export interface ConfigSDKOptions {
    configDir?: string;  // For AppYamlConfig
    configPath?: string; // For standalone single file
    contextExtenders?: ContextExtender[];
    validateSchema?: boolean; // Reserved for future validation logic
}

export class ConfigSDK {
    private static instance: ConfigSDK;
    private logger: Logger;
    private appYaml: any;
    private registry: any; // ContextRegistry instance
    private resolver: any; // ContextResolver instance
    private contextExtenders: ContextExtender[];

    // State
    private rawConfig: any;
    private initialized: boolean = false;

    private constructor(options: ConfigSDKOptions) {
        this.logger = Logger.create('config-sdk', 'sdk.ts');
        this.contextExtenders = options.contextExtenders || [];
    }

    // Recommendation 1: Async Initialize
    public static async initialize(options: ConfigSDKOptions = {}): Promise<ConfigSDK> {
        if (ConfigSDK.instance) {
            return ConfigSDK.instance;
        }

        const sdk = new ConfigSDK(options);
        await sdk.bootstrap(options);
        ConfigSDK.instance = sdk;
        return sdk;
    }

    public static getInstance(): ConfigSDK {
        if (!ConfigSDK.instance) {
            throw new Error("ConfigSDK not initialized. Call initialize() first.");
        }
        return ConfigSDK.instance;
    }

    private async bootstrap(options: ConfigSDKOptions) {
        this.logger.debug("Bootstrapping ConfigSDK...");

        // 1. Load Static Config
        // In a real scenario, this might need dynamic import or injection if AppYamlConfig isn't global
        // Assuming AppYamlConfig is the standard singleton pattern for now.
        const appYamlInstance = AppYamlConfig.getInstance();

        // Ideally, AppYamlConfig should expose a way to set configDir if not already set.
        // For standalone, we might simply be reading a file if AppYamlConfig supports it.

        this.rawConfig = appYamlInstance.getAll();
        this.logger.debug("Raw config loaded", { keys: Object.keys(this.rawConfig) });

        // 2. Setup Resolver (Assuming runtime-template-resolver pattern)
        // We need the registry. In standard server, this is global or passed in.
        // For this SDK, we might need to rely on the environment being set previously,
        // OR create a new empty registry if standalone.

        // NOTE: This implementation assumes the Registry is populated elsewhere (autoloading).
        // If standalone, we might need to manually trigger autoload.

        // For now, we'll assume we can pass a registry or import the default one if available.
        // Since we don't have a direct 'Registry' import here, we rely on the `createResolver` factory.
        // In a full implementation, we'd import { globalRegistry } from 'runtime-template-resolver/registry'.

        // Placeholder for registry access - assuming passed via options or implicitly global for prototype.
        this.registry = { list: () => [] }; // config-sdk acts as consumer, not registry owner usually.

        this.initialized = true;
    }

    public getRaw(): any {
        return this.rawConfig;
    }

    public async getResolved(scope: ComputeScope, request?: FastifyRequest): Promise<any> {
        if (!this.initialized) throw new Error("SDK not initialized");

        const context = await ContextBuilder.build({
            config: this.rawConfig,
            app: this.rawConfig.app || {},
            request: request
        }, this.contextExtenders);

        // Create a NEW resolver instance for this resolution (standard pattern)
        // In v800 `runtime_template_resolver`, createResolver takes a registry.
        // We might need to ensure we have that registry.
        const resolver = createResolver(this.registry); // Using the registry we have/found

        const resolved = await resolver.resolveObject(
            this.rawConfig,
            context,
            scope
        );

        // Merge overwrites is currently implicit in 'resolveObject' if it follows v800 spec
        // But if we need explicit post-process merging (Feature 2.3):
        return applyOverwrites(resolved, resolved.overwrite_from_context);
    }

    public async toJSON(options: { maskSecrets?: boolean } = {}): Promise<any> {
        // Basic export
        return this.getRaw();
    }
}
