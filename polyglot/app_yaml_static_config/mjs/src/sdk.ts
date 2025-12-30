import { glob } from 'glob';
import * as path from 'path';
import { AppYamlConfig } from './core.js';
import { InitOptions } from './types.js';

export class AppYamlConfigSDK {
    private config: AppYamlConfig;

    constructor(config: AppYamlConfig) {
        this.config = config;
    }

    static async fromDirectory(configDir: string): Promise<AppYamlConfigSDK> {
        const files = await glob(path.join(configDir, "*.yaml"));
        await AppYamlConfig.initialize({ files, configDir });
        return new AppYamlConfigSDK(AppYamlConfig.getInstance());
    }

    get(key: string): unknown {
        const value = this.config.get(key);
        return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
    }

    getNested(keys: string[]): unknown {
        const value = this.config.getNested(keys);
        return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
    }

    getAll(): Record<string, unknown> {
        return JSON.parse(JSON.stringify(this.config.getAll()));
    }

    listProviders(): string[] {
        const providers = this.config.get<Record<string, unknown>>('providers') ?? {};
        return Object.keys(providers);
    }

    listServices(): string[] {
        const services = this.config.get<Record<string, unknown>>('services') ?? {};
        return Object.keys(services);
    }

    listStorages(): string[] {
        const storages = this.config.get<Record<string, unknown>>('storages') ?? {};
        return Object.keys(storages);
    }
}
