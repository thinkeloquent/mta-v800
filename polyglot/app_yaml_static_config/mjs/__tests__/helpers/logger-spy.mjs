/**
 * Test utilities for logger spying and verification.
 */

/**
 * Create a logger spy that captures all log calls.
 * @returns {Object} Object with logs and mockLogger
 */
export function createLoggerSpy() {
    const logs = { debug: [], info: [], warn: [], error: [], trace: [] };
    const mockLogger = {
        debug: (msg, ...args) => logs.debug.push({ msg, args }),
        info: (msg, ...args) => logs.info.push({ msg, args }),
        warn: (msg, ...args) => logs.warn.push({ msg, args }),
        error: (msg, ...args) => logs.error.push({ msg, args }),
        trace: (msg, ...args) => logs.trace.push({ msg, args }),
    };
    return { logs, mockLogger };
}

/**
 * Assert that logs contain expected text at specified level.
 * @param {Object} logs - The logs object from createLoggerSpy
 * @param {string} level - Log level (debug, info, warn, error, trace)
 * @param {string} text - Text to search for
 * @returns {boolean}
 */
export function expectLogContains(logs, level, text) {
    const found = logs[level].some(entry => entry.msg.includes(text));
    if (!found) {
        throw new Error(
            `Expected log containing '${text}' at level '${level}' not found.\n` +
            `Captured ${level} logs: ${JSON.stringify(logs[level])}`
        );
    }
    return true;
}

/**
 * Get path to fixtures directory.
 * @returns {string}
 */
export function getFixturesDir() {
    return new URL('../../__fixtures__', import.meta.url).pathname.replace(/^\/([A-Z]:)/, '$1');
}
