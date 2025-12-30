import { LoadResult } from './domain.js';

export interface SDKInfo {
    version: string;
    language: 'python' | 'node';
}

export interface SDKResult<T> {
    success: boolean;
    data?: T;
    error?: {
        code: string;
        message: string;
        details?: Record<string, unknown>;
    };
}

export interface ConfigDescription {
    version: string;
    varsCount: number;
    sources: string[];
}

export interface SecretInfo {
    key: string;
    masked: string;
    exists: boolean;
}

export interface ValidationResult {
    valid: boolean;
    errors: string[];
    warnings: string[];
}

export interface DiagnosticResult {
    initialized: boolean;
    varsLoaded: number;
    issues: string[];
}

export interface IVaultFileSDK {
    // CLI Operations
    loadFromPath(path: string): Promise<SDKResult<LoadResult>>;
    validateFile(path: string): Promise<SDKResult<ValidationResult>>;
    exportToFormat(format: 'json' | 'yaml', path: string): Promise<SDKResult<void>>;

    // Agent Operations
    describeConfig(): SDKResult<ConfigDescription>;
    getSecretSafe(key: string): SDKResult<SecretInfo>;
    listAvailableKeys(): SDKResult<string[]>;

    // DEV Tool Operations
    diagnoseEnvStore(): SDKResult<DiagnosticResult>;
    findMissingRequired(keys: string[]): SDKResult<string[]>;
    suggestMissingKeys(partial: string): SDKResult<string[]>;
}
