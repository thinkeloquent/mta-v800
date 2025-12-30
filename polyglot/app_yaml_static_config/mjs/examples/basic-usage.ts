/**
 * Basic Usage Example for app-yaml-static-config
 *
 * This script demonstrates the core functionality of the AppYamlConfig singleton,
 * including initialization, retrieving values, exploring usage of the SDK layer,
 * and verifying immutability.
 */

import * as path from 'path';
import { fileURLToPath } from 'url';
import { AppYamlConfig, AppYamlConfigSDK } from '../src/index.js';
import { ImmutabilityError } from '../dist/validators.js'; // Importing from dist for type check or direct error

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, '..', '__fixtures__');

async function main() {
    console.log('=============================================================================');
    console.log('App Yaml Static Config - Basic Usage Example');
    console.log('=============================================================================\n');

    await example1_initialization();
    await example2_retrieving_values();
    await example3_nested_access();
    await example4_sdk_usage();
    await example5_immutability();
}

// =============================================================================
// Example 1: Initialization
// =============================================================================
/**
 * Demonstrates how to initialize the singleton with specific configuration files.
 */
async function example1_initialization() {
    console.log('[Example 1] Initialization');

    // We point to the fixtures directory for demo purposes
    const configFile = path.join(FIXTURES_DIR, 'base.yaml');

    // Initialize the singleton
    // Note: In a real app, this is done once at startup
    const instance = await AppYamlConfig.initialize({
        files: [configFile],
        configDir: FIXTURES_DIR,
    });

    console.log('✅ Singleton initialized successfully.');
    console.log(`   Config loaded from: ${configFile}\n`);
}

// =============================================================================
// Example 2: Retrieving Values
// =============================================================================
/**
 * Demonstrates retrieving top-level values and using defaults.
 */
async function example2_retrieving_values() {
    console.log('[Example 2] Retrieving Values');

    const config = AppYamlConfig.getInstance();

    // Get a known key
    const appConfig = config.get('app');
    console.log('   Value for "app":', appConfig);

    // Get a missing key with default
    const missing = config.get('non_existent_key', 'default_value');
    console.log('   Value for "non_existent_key" (defaulted):', missing);
    console.log('');
}

// =============================================================================
// Example 3: Nested Access
// =============================================================================
/**
 * Demonstrates accessing deeply nested keys safely.
 */
async function example3_nested_access() {
    console.log('[Example 3] Nested Access');

    const config = AppYamlConfig.getInstance();

    // Using array path for safe navigation
    const appName = config.getNested(['app', 'name']);
    console.log('   Value for ["app", "name"]:', appName);

    // Missing nested path with default
    const deepMissing = config.getNested(['deeply', 'missing', 'path'], 'fallback_val');
    console.log('   Value for missing nested path:', deepMissing);
    console.log('');
}

// =============================================================================
// Example 4: SDK Usage
// =============================================================================
/**
 * Demonstrates using the SDK layer for controlled access (e.g., for external tools).
 */
async function example4_sdk_usage() {
    console.log('[Example 4] SDK Usage');

    const sdk = new AppYamlConfigSDK();

    // SDK methods mirror the main instance but are often used for tooling
    const allConfig = sdk.getAll();
    console.log('   SDK.getAll() keys:', Object.keys(allConfig));
    console.log('');
}

// =============================================================================
// Example 5: Immutability
// =============================================================================
/**
 * Demonstrates that the configuration cannot be modified at runtime.
 */
async function example5_immutability() {
    console.log('[Example 5] Immutability Verification');

    const config = AppYamlConfig.getInstance();

    try {
        console.log('   Attempting to set a new value...');
        // @ts-ignore - purposefully ignoring TS error to show runtime check
        config.set('new_key', 'value');
    } catch (error) {
        if (error instanceof ImmutabilityError || error.name === 'ImmutabilityError') {
            console.log('✅ Caught expected ImmutabilityError:', error.message);
        } else {
            console.error('❌ Unexpected error:', error);
        }
    }
    console.log('');
}

main().catch(err => {
    console.error('Unhandled error in example:', err);
    process.exit(1);
});
