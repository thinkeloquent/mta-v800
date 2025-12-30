/**
 * Basic usage examples for vault_file package.
 *
 * This package provides Vault File management and Environment Store logic.
 */
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import { VaultFileSDK, EnvStore } from '../src/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ensure we have a dummy .env file for demonstration
const DEMO_ENV_FILE = path.join(__dirname, '.env.example');
if (!fs.existsSync(DEMO_ENV_FILE)) {
    fs.writeFileSync(DEMO_ENV_FILE, 'EXAMPLE_VAR=hello_world\\nANOTHER_VAR=foo_bar');
}

// =============================================================================
// Example 1: SDK Initialization and Config Loading
// =============================================================================
/**
 * Initialize the SDK and load configuration from a specific .env file.
 */
async function example1_loadConfig(): Promise<void> {
    console.log('--- Example 1: Load Config ---');

    // Create SDK instance using builder
    const sdk = VaultFileSDK.create()
        .withEnvPath(DEMO_ENV_FILE)
        .build();

    // Load config (initializes EnvStore)
    const result = await sdk.loadConfig();

    if (result.success) {
        console.log('Config loaded successfully:', result.data);
    } else {
        console.error('Failed to load config:', result.error);
    }
}

// =============================================================================
// Example 2: Accessing Secrets Wrapper
// =============================================================================
/**
 * Use the SDK helper to safely access secrets with masking support.
 */
function example2_accessSecrets(): void {
    console.log('\n--- Example 2: Access Secrets ---');

    // Re-use default SDK instance (EnvStore is singleton, already initialized in Ex 1)
    const sdk = VaultFileSDK.create().build();

    const secret = sdk.getSecretSafe('EXAMPLE_VAR');
    if (secret.success && secret.data) {
        console.log(`Key: ${secret.data.key}`);
        console.log(`Exists: ${secret.data.exists}`);
        console.log(`Masked Value: ${secret.data.masked}`);
    }
}

// =============================================================================
// Example 3: Direct EnvStore Usage
// =============================================================================
/**
 * Access variables directly via the EnvStore singleton for zero-overhead reads.
 */
function example3_envStoreUsage(): void {
    console.log('\n--- Example 3: Direct EnvStore Usage ---');

    // Get value or default
    const val = EnvStore.get('NON_EXISTENT', 'default_value');
    console.log('Got with default:', val);

    // Get existing value
    const existing = EnvStore.get('EXAMPLE_VAR');
    console.log('Got existing:', existing);

    // Get or throw
    try {
        const required = EnvStore.getOrThrow('EXAMPLE_VAR');
        console.log('Got required:', required);
    } catch (err: any) {
        console.error('Error getting required:', err.message);
    }
}

// =============================================================================
// Example 4: File Validation
// =============================================================================
/**
 * Validate a vault file or env file without loading it into the store.
 */
async function example4_validation(): Promise<void> {
    console.log('\n--- Example 4: Validation ---');

    const sdk = VaultFileSDK.create().build();
    const validation = await sdk.validateFile(DEMO_ENV_FILE);

    if (validation.success && validation.data) {
        console.log(`File ${path.basename(DEMO_ENV_FILE)} valid:`, validation.data.valid);
    }
}

// =============================================================================
// Main Runner
// =============================================================================
async function main(): Promise<void> {
    try {
        await example1_loadConfig();
        example2_accessSecrets();
        example3_envStoreUsage();
        await example4_validation();

        // Cleanup
        if (fs.existsSync(DEMO_ENV_FILE)) {
            fs.unlinkSync(DEMO_ENV_FILE);
        }
    } catch (err) {
        console.error('Unhandled error in examples:', err);
    }
}

main();
