import { SecurityError, ErrorCode } from './errors.js';

export class Security {
    private static PATH_PATTERN = /^[a-zA-Z][a-zA-Z0-9_.]*$/;

    private static BLOCKED_PATTERNS = new Set([
        '__proto__',
        '__class__',
        '__dict__',
        'constructor',
        'prototype'
    ]);

    public static validatePath(path: string): void {
        if (!path) {
            throw new SecurityError('Path cannot be empty', ErrorCode.SECURITY_BLOCKED_PATH);
        }

        if (!Security.PATH_PATTERN.test(path)) {
            throw new SecurityError(
                `Invalid path: ${path}. Must start with letter and contain only alphanumeric, underscore, or dot.`,
                ErrorCode.SECURITY_BLOCKED_PATH,
                { path }
            );
        }

        if (path.includes('..')) {
            throw new SecurityError(
                'Path traversal not allowed (..)',
                ErrorCode.SECURITY_BLOCKED_PATH,
                { path }
            );
        }

        const segments = path.split('.');
        for (const segment of segments) {
            if (Security.BLOCKED_PATTERNS.has(segment)) {
                throw new SecurityError(
                    `Path contains blocked segment: ${segment}`,
                    ErrorCode.SECURITY_BLOCKED_PATH,
                    { path, segment }
                );
            }
            if (segment.startsWith('_')) {
                throw new SecurityError(
                    `Path segment starts with underscore: ${segment}`,
                    ErrorCode.SECURITY_BLOCKED_PATH,
                    { path, segment }
                );
            }
        }
    }
}
