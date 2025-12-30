/** @type {import('jest').Config} */
module.exports = {
    testEnvironment: 'node',
    roots: ['<rootDir>/__tests__'],
    testMatch: ['**/*.test.mjs'],
    moduleFileExtensions: ['mjs', 'js', 'json'],
    transform: {},
    // Run tests serially to avoid port conflicts
    maxWorkers: 1,
    collectCoverageFrom: [
        'src/**/*.mjs',
        '!src/main.mjs',
    ],
    coverageThreshold: {
        global: {
            branches: 70,
            functions: 70,
            lines: 70,
            statements: 70,
        },
    },
    testTimeout: 30000,
};
