import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        include: ['__tests__/**/*.test.{ts,mjs}'],
        environment: 'node',
        globals: true,
    },
    resolve: {
        extensions: ['.ts', '.js', '.mjs'],
    },
});
