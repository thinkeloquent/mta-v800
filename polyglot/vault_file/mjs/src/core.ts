import yaml from 'js-yaml';
import fs from 'fs';
import { VaultFile } from './domain.js';

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
    const transformed = transformKeys(vaultFile, toSnakeCase);
    return JSON.stringify(transformed, null, 2);
}

export function fromJSON(jsonStr: string): any {
    const parsed = JSON.parse(jsonStr);
    const transformed = transformKeys(parsed, toCamelCase);

    // Normalize version if present
    if (transformed.header && transformed.header.version) {
        transformed.header.version = normalizeVersion(transformed.header.version);
    }

    return transformed;
}

export function parseEnvFile(filePath: string): Record<string, string> {
    if (!fs.existsSync(filePath)) {
        return {};
    }
    const content = fs.readFileSync(filePath, 'utf-8');
    // Simple parsing matching python logic roughly, or use dotenv.
    // Use dotenv for robustness if permitted, but we have dotenv dependency.
    // Requirement says logic to parse .env.
    // Let's use simple logic to match our Python simple logic, OR use dotenv.parse
    // Plan says "dotenv: parse .env files".

    // Implementation note: dotenv.parse returns an object.
    // But dotenv doesn't support comment filtering exactly same way as custom?
    // Actually dotenv is standard. I'll use it or manual to match Python core.py exactly.
    // Python core.py implementation was manual.
    // Let's use manual to match Python's behavior if needed, or better, standard dotenv.
    // I will use strict manual implementation to avoid dep if simple, but I added dotenv to package.json.
    // Let's use dotenv for reliability.

    // Wait, I can't import 'dotenv' easily in ESM to just parse without configuring?
    // import { parse } from 'dotenv'; 
    // checking dotenv docs... yes, `import { parse } from 'dotenv'` works.

    // Actually, let's stick to the manual logic I wrote in python for strict parity if that was intent,
    // but standard library is better. I'll use manual to be safe on "no magic".

    const env: Record<string, string> = {};
    const lines = content.split('\n');
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) continue;
        const idx = trimmed.indexOf('=');
        if (idx !== -1) {
            const key = trimmed.substring(0, idx).trim();
            let val = trimmed.substring(idx + 1).trim();
            if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
                val = val.substring(1, val.length - 1);
            }
            env[key] = val;
        }
    }
    return env;
}
