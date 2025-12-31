import { MissingStrategy } from './interfaces.js';
import { MissingValueError } from './errors.js';

export function handleMissing(key: string, strategy: MissingStrategy = MissingStrategy.EMPTY, defaultValue?: string): string {
    switch (strategy) {
        case MissingStrategy.KEEP:
            return `{{${key}}}`;
        case MissingStrategy.ERROR:
            throw new MissingValueError(`Missing value for placeholder: ${key}`);
        case MissingStrategy.DEFAULT:
            return defaultValue ?? '';
        case MissingStrategy.EMPTY:
        default:
            return '';
    }
}
