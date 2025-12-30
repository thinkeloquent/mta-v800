import fs from 'fs';
import path from 'path';
import { EnvStore } from './env-store.js';
import { fromJSON, toJSON, parseEnvFile } from './core.js';
import { LoadResult } from './domain.js';
import {
    IVaultFileSDK,
    SDKResult,
    ConfigDescription,
    SecretInfo,
    ValidationResult,
    DiagnosticResult
} from './sdk-types.js';
import { Logger, IVaultFileLogger } from './logger.js';

export class VaultFileSDK implements IVaultFileSDK {
    private envPath: string = '.env';
    private base64Parsers: Record<string, (val: string) => any> = {};
    private log: IVaultFileLogger;

    private constructor() {
        this.log = Logger.create('vault-file', 'sdk.ts');
    }

    public static create(): VaultFileSDKBuilder {
        return new VaultFileSDKBuilder();
    }

    // Builder methods implementation moved to Builder class or internal setter
    // For simplicity, let's allow builder to construct this.
    public setEnvPath(path: string) {
        this.envPath = path;
    }

    public setBase64Parsers(parsers: Record<string, (val: string) => any>) {
        this.base64Parsers = parsers;
    }

    private success<T>(data?: T): SDKResult<T> {
        return { success: true, data };
    }

    private failure<T>(message: string, code: string = 'UNKNOWN_ERROR', details?: any): SDKResult<T> {
        this.log.error(`SDK operation failed: [${code}] ${message}`, details);
        return {
            success: false,
            error: { code, message, details }
        };
    }

    // CLI Operations
    public async loadConfig(): Promise<SDKResult<LoadResult>> {
        this.log.info('loadConfig() called', { envPath: this.envPath });
        try {
            const result = await EnvStore.onStartup(this.envPath);
            this.log.info('loadConfig() succeeded', { totalVarsLoaded: result.totalVarsLoaded });
            return this.success(result);
        } catch (err: any) {
            this.log.error('loadConfig() failed', err);
            return this.failure(err.message, 'LOAD_ERROR');
        }
    }

    public async loadFromPath(filePath: string): Promise<SDKResult<LoadResult>> {
        this.log.info('loadFromPath() called', { filePath });

        if (!filePath) {
            this.log.error('loadFromPath() called with empty filePath');
            return this.failure('File path is required', 'INVALID_ARGUMENT');
        }

        try {
            if (!fs.existsSync(filePath)) {
                this.log.warn('loadFromPath() file not found', { filePath });
                return this.failure(`File not found: ${filePath}`, 'FILE_NOT_FOUND');
            }

            this.log.debug('Parsing env file', { filePath });
            const vars = parseEnvFile(filePath);
            const count = Object.keys(vars).length;
            this.log.info('loadFromPath() succeeded', { filePath, totalVarsLoaded: count });
            return this.success({ totalVarsLoaded: count });

        } catch (err: any) {
            this.log.error('loadFromPath() failed', { filePath }, err);
            return this.failure(err.message, 'LOAD_ERROR');
        }
    }

    public async validateFile(filePath: string): Promise<SDKResult<ValidationResult>> {
        this.log.info('validateFile() called', { filePath });

        if (!filePath) {
            this.log.error('validateFile() called with empty filePath');
            return this.failure('File path is required', 'INVALID_ARGUMENT');
        }

        if (!fs.existsSync(filePath)) {
            this.log.warn('validateFile() file not found', { filePath });
            return this.failure(`File not found: ${filePath}`, 'FILE_NOT_FOUND');
        }

        try {
            this.log.debug('Attempting to parse file for validation', { filePath });
            parseEnvFile(filePath);
            this.log.info('validateFile() succeeded - file is valid', { filePath });
            return this.success({
                valid: true,
                errors: [],
                warnings: []
            });
        } catch (err: any) {
            this.log.warn('validateFile() found invalid file', { filePath, error: err.message });
            return this.success({
                valid: false,
                errors: [err.message],
                warnings: []
            });
        }
    }

    public async exportToFormat(format: 'json' | 'yaml', filePath: string): Promise<SDKResult<void>> {
        this.log.info('exportToFormat() called', { format, filePath });
        this.log.warn('exportToFormat() not implemented');
        return this.failure('Not implemented', 'NOT_IMPLEMENTED');
    }

    // Agent Operations
    public describeConfig(): SDKResult<ConfigDescription> {
        this.log.debug('describeConfig() called');
        const varsCount = EnvStore.getInstance()['_totalVarsLoaded'] || 0;
        this.log.debug('describeConfig() returning', { varsCount, sources: [this.envPath] });
        return this.success({
            version: '1.0.0',
            varsCount,
            sources: [this.envPath]
        });
    }

    public getSecretSafe(key: string): SDKResult<SecretInfo> {
        this.log.debug('getSecretSafe() called', { key });
        if (!key) {
            this.log.warn('getSecretSafe() called with empty key');
        }
        const val = EnvStore.get(key);
        const exists = val !== undefined;
        this.log.debug('getSecretSafe() result', { key, exists });
        return this.success({
            key,
            exists,
            masked: exists ? '***' : ''
        });
    }

    public listAvailableKeys(): SDKResult<string[]> {
        this.log.debug('listAvailableKeys() called');
        this.log.warn('listAvailableKeys() not fully implemented - returning empty array');
        return this.success([]);
    }

    // DEV Tool Operations
    public diagnoseEnvStore(): SDKResult<DiagnosticResult> {
        this.log.debug('diagnoseEnvStore() called');
        const initialized = EnvStore.isInitialized();
        this.log.info('diagnoseEnvStore() result', { initialized });
        return this.success({
            initialized,
            varsLoaded: 0,
            issues: []
        });
    }

    public findMissingRequired(keys: string[]): SDKResult<string[]> {
        this.log.info('findMissingRequired() called', { keysCount: keys?.length ?? 0 });
        if (!keys || keys.length === 0) {
            this.log.debug('findMissingRequired() no keys to check');
            return this.success([]);
        }
        const missing = keys.filter(k => EnvStore.get(k) === undefined);
        if (missing.length > 0) {
            this.log.warn('findMissingRequired() found missing keys', { missingKeys: missing });
        } else {
            this.log.debug('findMissingRequired() all keys present');
        }
        return this.success(missing);
    }

    public suggestMissingKeys(partial: string): SDKResult<string[]> {
        this.log.debug('suggestMissingKeys() called', { partial });
        this.log.warn('suggestMissingKeys() not implemented - returning empty array');
        return this.success([]);
    }
}

export class VaultFileSDKBuilder {
    private sdk: VaultFileSDK;

    constructor() {
        // @ts-ignore - access private constructor
        this.sdk = new VaultFileSDK();
    }

    public withEnvPath(path: string): VaultFileSDKBuilder {
        this.sdk.setEnvPath(path);
        return this;
    }

    public withBase64Parsers(parsers: Record<string, (val: string) => any>): VaultFileSDKBuilder {
        this.sdk.setBase64Parsers(parsers);
        return this;
    }

    public build(): VaultFileSDK {
        return this.sdk;
    }
}
