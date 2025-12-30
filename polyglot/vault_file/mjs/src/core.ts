import yaml from 'js-yaml';
import fs from 'fs';
import { VaultFile } from './domain.js';
import { Logger, IVaultFileLogger } from './logger.js';

const log: IVaultFileLogger = Logger.create('vault-file', 'core.ts');

/**
 * Convert camelCase string to snake_case
 */
function toSnakeCase(str: string): string {
    return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
}

/**
 * Convert snake_case string to camelCase
 */
function toCamelCase(str: string): string {
    return str.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
}

/**
 * Recursively transform keys
 */
function transformKeys(obj: any, transformer: (key: string) => string): any {
    if (Array.isArray(obj)) {
        return obj.map(v => transformKeys(v, transformer));
    } else if (obj !== null && obj.constructor === Object) {
        return Object.keys(obj).reduce((result, key) => {
            result[transformer(key)] = transformKeys(obj[key], transformer);
            return result;
        }, {} as any);
    }
    return obj;
}

// Normalize version to x.y.z
function normalizeVersion(version: string): string {
    const parts = version.split('.');
    while (parts.length < 3) parts.push('0');
    return parts.slice(0, 3).join('.');
}

export function toJSON(vaultFile: VaultFile): string {
    log.debug('Converting VaultFile to JSON');
    try {
        const transformed = transformKeys(vaultFile, toSnakeCase);
        const result = JSON.stringify(transformed, null, 2);
        log.debug('Successfully converted VaultFile to JSON', { length: result.length });
        return result;
    } catch (err) {
        log.error('Failed to convert VaultFile to JSON', err);
        throw err;
    }
}

export function fromJSON(jsonStr: string): any {
    log.debug('Parsing JSON to VaultFile', { inputLength: jsonStr?.length ?? 0 });

    if (!jsonStr || typeof jsonStr !== 'string') {
        log.error('Invalid JSON input: input is empty or not a string');
        throw new Error('Invalid JSON input: input is empty or not a string');
    }

    try {
        const parsed = JSON.parse(jsonStr);
        log.debug('JSON parsed successfully');

        const transformed = transformKeys(parsed, toCamelCase);

        // Normalize version if present
        if (transformed.header && transformed.header.version) {
            const originalVersion = transformed.header.version;
            transformed.header.version = normalizeVersion(transformed.header.version);
            log.debug('Normalized version', { from: originalVersion, to: transformed.header.version });
        }

        log.debug('Successfully parsed JSON to VaultFile structure');
        return transformed;
    } catch (err) {
        log.error('Failed to parse JSON', err);
        throw err;
    }
}

export function parseEnvFile(filePath: string): Record<string, string> {
    log.debug('Attempting to parse env file', { filePath });

    if (!filePath) {
        log.error('parseEnvFile called with empty or null filePath');
        throw new Error('File path is required');
    }

    if (!fs.existsSync(filePath)) {
        log.warn('Env file not found, returning empty object', { filePath });
        return {};
    }

    log.info('Loading env file', { filePath });

    let content: string;
    try {
        content = fs.readFileSync(filePath, 'utf-8');
        log.debug('File read successfully', { filePath, contentLength: content.length });
    } catch (err) {
        log.error('Failed to read env file', { filePath }, err as Error);
        throw err;
    }

    if (!content || content.trim().length === 0) {
        log.warn('Env file is empty', { filePath });
        return {};
    }

    const env: Record<string, string> = {};
    const lines = content.split('\n');
    let lineNumber = 0;
    let parsedCount = 0;
    let skippedCount = 0;
    let errorCount = 0;

    for (const line of lines) {
        lineNumber++;
        const trimmed = line.trim();

        // Skip empty lines and comments
        if (!trimmed || trimmed.startsWith('#')) {
            skippedCount++;
            continue;
        }

        const idx = trimmed.indexOf('=');
        if (idx === -1) {
            log.warn('Skipping malformed line (no "=" found)', { filePath, lineNumber, line: trimmed });
            errorCount++;
            continue;
        }

        const key = trimmed.substring(0, idx).trim();
        if (!key) {
            log.warn('Skipping line with empty key', { filePath, lineNumber, line: trimmed });
            errorCount++;
            continue;
        }

        let val = trimmed.substring(idx + 1).trim();

        // Remove surrounding quotes
        if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
            val = val.substring(1, val.length - 1);
        }

        env[key] = val;
        parsedCount++;
        log.debug('Parsed env var', { key, lineNumber });
    }

    log.info('Finished parsing env file', {
        filePath,
        totalLines: lineNumber,
        parsedVars: parsedCount,
        skippedLines: skippedCount,
        malformedLines: errorCount
    });

    if (errorCount > 0) {
        log.warn('Some lines could not be parsed', { filePath, malformedLines: errorCount });
    }

    return env;
}
