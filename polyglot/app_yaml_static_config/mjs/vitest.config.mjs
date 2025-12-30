import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        include: ['__tests__/**/*.test.mjs'],
        globals: true,
        environment: 'node',
        testTimeout: 10000,
        hookTimeout: 10000,
        coverage: {
            provider: 'v8',
            reporter: ['text', 'html'],
            include: ['dist/**/*.js'],
            exclude: ['__tests__/**', 'node_modules/**'],
        },
    },
});
