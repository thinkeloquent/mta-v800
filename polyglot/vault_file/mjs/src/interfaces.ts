import { VaultHeader, LoadResult } from './domain.js';
import { IVaultFileLogger } from './logger.js';

export interface IVaultFile {
    header: VaultHeader;
    secrets: Record<string, string>;
}

export interface IEnvStore {
    get(key: string, defaultValue?: string): string | undefined;
    getOrThrow(key: string): string;
    isInitialized(): boolean;
    onStartup(envFile?: string): Promise<LoadResult>;
}

export { IVaultFileLogger };
