/**
 * Utility to reset the AppYamlConfig singleton between tests.
 */

/**
 * Reset the AppYamlConfig singleton.
 * This is needed because the singleton persists across test files.
 */
export function resetAppYamlConfigSingleton() {
    // We need to access the private static field
    // This is a workaround for testing singletons
    try {
        const { AppYamlConfig } = require('../../dist/core.js');
        AppYamlConfig._instance = null;
    } catch (e) {
        // Module might not be built yet
    }
}
