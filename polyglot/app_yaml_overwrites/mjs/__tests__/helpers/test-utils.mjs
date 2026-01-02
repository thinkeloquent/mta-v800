/**
 * Test utilities and shared helpers for app_yaml_overwrites tests.
 */

/**
 * Creates a mock logger with spy functions for testing.
 * @returns {{ logs: object, mockLogger: object }}
 */
export function createLoggerSpy() {
    const logs = { trace: [], debug: [], info: [], warn: [], error: [] };
    const mockLogger = {
        debug: (msg, data) => logs.debug.push({ msg, data }),
        info: (msg, data) => logs.info.push({ msg, data }),
        warn: (msg, data) => logs.warn.push({ msg, data }),
        error: (msg, data) => logs.error.push({ msg, data }),
        trace: (msg, data) => logs.trace.push({ msg, data }),
    };
    return { logs, mockLogger };
}

/**
 * Asserts that a log entry contains the expected text.
 * @param {object} logs - The logs object from createLoggerSpy
 * @param {string} level - The log level to check
 * @param {string} text - The text to find
 * @throws {Error} If the text is not found
 */
export function expectLogContains(logs, level, text) {
    const found = logs[level].some(entry =>
        entry.msg.includes(text) || JSON.stringify(entry.data || {}).includes(text)
    );
    if (!found) {
        const allLogs = logs[level].map(e => `${e.msg} ${JSON.stringify(e.data || {})}`).join('\n');
        throw new Error(`Expected log containing '${text}' not found.\nCaptured ${level} logs:\n${allLogs}`);
    }
}

/**
 * Creates a sample configuration for testing.
 * @returns {object}
 */
export function createSampleConfig() {
    return {
        app: {
            name: "Test App",
            version: "1.0.0"
        },
        providers: {
            test_provider: {
                base_url: "https://api.test.com",
                headers: {
                    "X-App-Name": null,
                    "X-Custom": "static-value"
                },
                overwrite_from_context: {
                    headers: {
                        "X-App-Name": "{{app.name}}",
                        "X-Token": "{{fn:compute_token}}"
                    }
                }
            }
        },
        storage: {
            redis: {
                host: "localhost",
                port: 6379
            }
        }
    };
}

/**
 * Creates a mock AppYamlConfig for testing.
 * @param {object} config - The config to return from getAll()
 * @returns {object}
 */
export function createMockAppYamlConfig(config = {}) {
    return {
        getAll: () => config,
        getInstance: function() { return this; }
    };
}

/**
 * Creates a mock Fastify request object.
 * @param {object} options - Request options
 * @returns {object}
 */
export function createMockRequest(options = {}) {
    return {
        headers: options.headers || {},
        query: options.query || {},
        params: options.params || {},
        body: options.body || {},
        state: options.state || {},
        id: options.id || 'test-request-id'
    };
}

/**
 * Wait for a specified number of milliseconds.
 * @param {number} ms - Milliseconds to wait
 * @returns {Promise<void>}
 */
export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
