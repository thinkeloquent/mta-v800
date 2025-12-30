/**
 * Test utilities and helpers for server tests.
 */

/**
 * Create a mock logger that captures all log calls.
 * @returns {{ logs: Object, mockLogger: Object }}
 */
export function createLoggerSpy() {
    const logs = {
        log: [],
        debug: [],
        info: [],
        warn: [],
        error: [],
        trace: [],
    };

    const mockLogger = {
        log: (msg, data, err) => logs.log.push({ msg, data, err }),
        debug: (msg, data, err) => logs.debug.push({ msg, data, err }),
        info: (msg, data, err) => logs.info.push({ msg, data, err }),
        warn: (msg, data, err) => logs.warn.push({ msg, data, err }),
        error: (msg, data, err) => logs.error.push({ msg, data, err }),
        trace: (msg, data, err) => logs.trace.push({ msg, data, err }),
        packageName: 'test',
        filename: 'test.mjs',
        level: 'trace',
        child: () => mockLogger,
        withContext: () => mockLogger,
    };

    return { logs, mockLogger };
}

/**
 * Assert that logs contain a specific message.
 * @param {Object} logs - The captured logs
 * @param {string} level - The log level to check
 * @param {string} text - The text to search for
 */
export function expectLogContains(logs, level, text) {
    const found = logs[level].some(entry =>
        entry.msg && entry.msg.includes(text)
    );
    if (!found) {
        const allLogs = logs[level].map(e => e.msg).join(', ');
        throw new Error(`Expected log containing '${text}' not found. Logs: [${allLogs}]`);
    }
}

/**
 * Create a mock output function that captures output.
 * @returns {{ captured: string[], output: Object }}
 */
export function createOutputCapture() {
    const captured = [];
    const output = {
        log: (msg) => captured.push(msg),
        error: (msg) => captured.push(msg),
    };
    return { captured, output };
}

/**
 * Create temporary test directory.
 * @returns {Promise<string>}
 */
export async function createTempDir() {
    const { mkdtemp } = await import('fs/promises');
    const { tmpdir } = await import('os');
    const path = await import('path');
    return mkdtemp(path.join(tmpdir(), 'server-test-'));
}

/**
 * Clean up temporary test directory.
 * @param {string} dir
 */
export async function cleanupTempDir(dir) {
    const { rm } = await import('fs/promises');
    await rm(dir, { recursive: true, force: true });
}
