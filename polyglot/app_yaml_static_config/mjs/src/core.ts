import * as fs from 'fs';
import * as yaml from 'js-yaml';
import merge from 'lodash.merge';
import { InitOptions, ILogger } from './types.js';
import { create as createLogger } from './logger.js';
import { ImmutabilityError } from './validators.js';

export class AppYamlConfig {
    private static _instance: AppYamlConfig | null = null;
    private _config: Record<string, any> = {};
    private _originalConfigs: Map<string, Record<string, any>> = new Map();
    private _initialMergedConfig: Record<string, any> | null = null;
    private _logger: ILogger;

    private constructor(options: InitOptions) {
        if (AppYamlConfig._instance) {
            throw new Error("This class is a singleton!");
        }
        this._logger = options.logger || createLogger("app-yaml-static-config", "core.ts");
        // Normalize appEnv to lowercase (e.g., "DEV" -> "dev")
        const normalizedOptions: InitOptions = {
            ...options,
            appEnv: options.appEnv?.toLowerCase()
        };
        this._loadConfig(normalizedOptions);
        AppYamlConfig._instance = this;
    }

    static async initialize(options: InitOptions): Promise<AppYamlConfig> {
        if (!AppYamlConfig._instance) {
            new AppYamlConfig(options);
        }
        return AppYamlConfig._instance!;
    }

    static getInstance(): AppYamlConfig {
        if (!AppYamlConfig._instance) {
            throw new Error("AppYamlConfig not initialized");
        }
        return AppYamlConfig._instance;
    }

    private _loadConfig(options: InitOptions): void {
        this._logger.info("Initializing configuration", options.files);
        const mergedConfig: Record<string, any> = {};

        for (const filePath of options.files) {
            this._logger.debug(`Loading config file: ${filePath}`);
            try {
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const content = (yaml.load(fileContent) as Record<string, any>) || {};
                this._originalConfigs.set(filePath, structuredClone(content));
                merge(mergedConfig, content);
            } catch (error) {
                this._logger.error(`Failed to load user config: ${filePath}`, error);
                throw error;
            }
        }

        this._config = mergedConfig;
        this._initialMergedConfig = structuredClone(mergedConfig);
        this._logger.info("Configuration initialized successfully");
    }

    get<T>(key: string, defaultValue?: T): T | undefined {
        return (this._config[key] as T) ?? defaultValue;
    }

    getNested<T>(keys: string[], defaultValue?: T): T | undefined {
        let current: any = this._config;
        for (const key of keys) {
            if (current && typeof current === 'object' && key in current) {
                current = current[key];
            } else {
                return defaultValue;
            }
        }
        return current as T;
    }

    getAll(): Record<string, any> {
        return structuredClone(this._config);
    }

    getOriginal(file?: string): Record<string, any> | undefined {
        if (file) {
            return structuredClone(this._originalConfigs.get(file));
        }
        return undefined;
    }

    // Note: getOriginalAll wasn't strictly typed in plan but implied parity. 
    // Adding for parity with Python implementation
    getOriginalAll(): Map<string, Record<string, any>> {
        return structuredClone(this._originalConfigs);
    }

    restore(): void {
        if (this._initialMergedConfig) {
            this._config = structuredClone(this._initialMergedConfig);
        }
    }

    // Immutability Stubs
    set(key: string, value: any): never {
        throw new ImmutabilityError("Configuration is immutable");
    }

    update(updates: Record<string, any>): never {
        throw new ImmutabilityError("Configuration is immutable");
    }

    reset(): never {
        throw new ImmutabilityError("Configuration is immutable");
    }

    clear(): never {
        throw new ImmutabilityError("Configuration is immutable");
    }
}
