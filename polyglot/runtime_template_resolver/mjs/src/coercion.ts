import { logger } from './logger.js';

const log = logger.create('runtime-template-resolver', 'coercion.ts');

export function toString(value: unknown): string {
    if (value === null || value === undefined) {
        return '';
    }
    if (typeof value === 'object') {
        try {
            return JSON.stringify(value);
        } catch (e) {
            log.warn('Failed to stringify object', { error: String(e) });
            return '[object Object]';
        }
    }
    return String(value);
}
