import { Logger } from './logger.js';
import { ContextBuilder, ContextExtender, RequestLike } from './context-builder.js';
import { applyOverwrites } from './overwrite-merger.js';

// Re-export RequestLike for external use
export type { RequestLike };

/**
 * Compute scope for resolution.
 * STARTUP: Resolve at application startup (no request context)
 * REQUEST: Resolve per-request (has request context)
 */
export enum ComputeScope {
    STARTUP = 'STARTUP',
    REQUEST = 'REQUEST'
}

/**
 * Optional external config provider interface.
 * Implementations can provide config from various sources (YAML files, env, etc.)
 */
interface ConfigProvider {
    getAll(): any;
}

export interface ConfigSDKOptions {
    /** Initial config object (alternative to configProvider) */
    config?: any;
    /** External config provider (e.g., AppYamlConfig) */
    configProvider?: ConfigProvider;
    /** Directory for config files (reserved for future use) */
    configDir?: string;
    /** Path to single config file (reserved for future use) */
    configPath?: string;
    /** Context extenders for building resolution context */
    contextExtenders?: ContextExtender[];
    /** Reserved for future schema validation */
    validateSchema?: boolean;
}

export class ConfigSDK {
    private static instance: ConfigSDK | undefined;
    private logger: Logger;
    private configProvider?: ConfigProvider;
    private contextExtenders: ContextExtender[];

    // State
    private rawConfig: any;
    private initialized: boolean = false;

    constructor(options: ConfigSDKOptions = {}) {
        this.logger = Logger.create('config-sdk', 'sdk.ts');
        this.contextExtenders = options.contextExtenders || [];
        this.configProvider = options.configProvider;
        // Allow direct config injection
        if (options.config) {
            this.rawConfig = options.config;
        }
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

        // Load config from provider if available and not already set
        if (!this.rawConfig && this.configProvider) {
            this.rawConfig = this.configProvider.getAll();
        }

        // Default to empty config if none provided
        if (!this.rawConfig) {
            this.rawConfig = {};
            this.logger.debug("No config provided, using empty config");
        }

        this.logger.debug("Raw config loaded", { keys: Object.keys(this.rawConfig) });
        this.initialized = true;
    }

    public getRaw(): any {
        return this.rawConfig;
    }

    public async getResolved(scope: ComputeScope, request?: RequestLike): Promise<any> {
        if (!this.initialized) throw new Error("SDK not initialized");

        // Build context for resolution
        const context = await ContextBuilder.build({
            config: this.rawConfig,
            app: this.rawConfig.app || {},
            request: request
        }, this.contextExtenders);

        // Apply overwrites from context
        // Note: Full template resolution (e.g., {{ env.VAR }}) requires runtime_template_resolver
        // This standalone version handles the overwrite_from_context merging pattern
        const overwriteSection = this.rawConfig.overwrite_from_context;
        if (overwriteSection) {
            return applyOverwrites(this.rawConfig, overwriteSection);
        }

        return this.rawConfig;
    }

    public async toJSON(options: { maskSecrets?: boolean } = {}): Promise<any> {
        // Basic export
        return this.getRaw();
    }

    /**
     * Reset the singleton instance (primarily for testing).
     */
    public static resetInstance(): void {
        ConfigSDK.instance = undefined;
    }
}
