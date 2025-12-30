/**
 * Test utilities and shared helpers for vault_file tests.
 */
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
/**
 * Create a logger spy for testing log output.
 */
export function createLoggerSpy() {
    const logs = { debug: [], info: [], warn: [], error: [] };
    const mockLogger = {
        debug: (msg, data) => logs.debug.push({ msg, data }),
        info: (msg, data) => logs.info.push({ msg, data }),
        warn: (msg, data) => logs.warn.push({ msg, data }),
        error: (msg, data, err) => logs.error.push({ msg, data, err }),
        trace: (msg, data) => logs.debug.push({ msg, data }),
    };
    return { logs, mockLogger };
}
/**
 * Assert that logs contain expected text at specified level.
 */
export function expectLogContains(logs, level, text) {
    const found = logs[level].some(entry => entry.msg.includes(text));
    if (!found) {
        const allMessages = logs[level].map(e => e.msg).join('\n');
        throw new Error(`Expected log containing '${text}' not found at ${level} level.\n` +
            `Captured logs:\n${allMessages || '(none)'}`);
    }
}
/**
 * Create a temporary .env file with given content.
 * Returns the file path. Caller is responsible for cleanup.
 */
export function createTempEnvFile(content) {
    const tmpDir = os.tmpdir();
    const filePath = path.join(tmpDir, `test-env-${Date.now()}-${Math.random().toString(36).slice(2)}.env`);
    fs.writeFileSync(filePath, content, 'utf-8');
    return filePath;
}
/**
 * Clean up a temporary file.
 */
export function cleanupTempFile(filePath) {
    try {
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
        }
    }
    catch {
        // Ignore cleanup errors
    }
}
/**
 * Sample .env content for testing.
 */
export const sampleEnvContent = `# Sample environment file
DATABASE_URL=postgres://localhost:5432/db
API_KEY="secret-key-123"
DEBUG=true
EMPTY_VALUE=
QUOTED_VALUE='single quoted'
`;
/**
 * Sample VaultFile JSON for testing.
 */
export const sampleVaultFileJson = JSON.stringify({
    header: {
        version: '1.0.0',
        created_at: '2023-01-01T00:00:00.000Z',
    },
    secrets: {
        MY_SECRET: 'value',
    },
});
//# sourceMappingURL=test-utils.js.map