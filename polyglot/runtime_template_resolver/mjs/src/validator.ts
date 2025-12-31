import { ValidationError } from './errors.js';

export function validatePlaceholder(placeholder: string): void {
    if (!placeholder || placeholder.trim() === '') {
        throw new ValidationError('Placeholder cannot be empty');
    }
    // Basic validation: must be valid path
    // Allowing dots, brackets, quotes, alphanumeric, underscore, hyphen
    if (!/^[\w\-\.\[\]"']+$/.test(placeholder)) {
        throw new ValidationError(`Invalid characters in placeholder: ${placeholder}`);
    }

    if (placeholder.includes('..')) {
        throw new ValidationError(`Invalid path (empty segment): ${placeholder}`);
    }
}
