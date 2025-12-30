/**
 * Unit tests for logger module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 * - Error handling verification
 */
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import logger, { create, LOG_LEVELS } from '../src/logger.mjs';
import { createOutputCapture } from './helpers/test-utils.mjs';

describe('Logger', () => {
    // =========================================================================
    // Statement Coverage
    // =========================================================================

    describe('Statement Coverage', () => {
        it('should export create function', () => {
            expect(typeof create).toBe('function');
        });

        it('should export LOG_LEVELS constant', () => {
            expect(LOG_LEVELS).toBeDefined();
            expect(LOG_LEVELS.info).toBe(2);
        });

        it('should export default logger factory', () => {
            expect(logger).toBeDefined();
            expect(typeof logger.create).toBe('function');
        });

        it('should create logger instance', () => {
            const log = create('test-package', 'test.mjs');
            expect(log).toBeDefined();
            expect(log.packageName).toBe('test-package');
        });

        it('should extract filename from path', () => {
            const log = create('test', '/path/to/file.mjs');
            expect(log.filename).toBe('file.mjs');
        });

        it('should extract filename from file:// URL', () => {
            const log = create('test', 'file:///path/to/file.mjs');
            expect(log.filename).toBe('file.mjs');
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('Branch Coverage', () => {
        it('should handle empty filename', () => {
            const log = create('test', '');
            expect(log.filename).toBe('unknown');
        });

        it('should handle undefined filename', () => {
            const log = create('test', undefined);
            expect(log.filename).toBe('unknown');
        });

        it('should skip logs below current level', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', { level: 'warn', output });

            log.debug('Should not appear');
            log.info('Should not appear either');

            expect(captured.length).toBe(0);
        });

        it('should log at or above current level', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', { level: 'info', output });

            log.info('Should appear');
            log.warn('Should also appear');

            expect(captured.length).toBe(2);
        });

        it('should handle data as Error object', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', { level: 'error', output });

            const error = new Error('Test error');
            log.error('Error message', error);

            expect(captured.length).toBe(1);
            expect(captured[0]).toContain('Test error');
        });

        it('should handle data as object with error', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', { level: 'error', output });

            const error = new Error('Test error');
            log.error('Error message', { key: 'value' }, error);

            expect(captured.length).toBe(1);
            expect(captured[0]).toContain('key');
        });
    });

    // =========================================================================
    // All Log Levels
    // =========================================================================

    describe('All Log Levels', () => {
        let captured;
        let output;
        let log;

        beforeEach(() => {
            const result = createOutputCapture();
            captured = result.captured;
            output = result.output;
            log = create('test', 'test.mjs', { level: 'trace', output });
        });

        it('should log at trace level', () => {
            log.trace('Trace message');
            expect(captured.length).toBe(1);
            expect(captured[0]).toContain('TRACE');
        });

        it('should log at debug level', () => {
            log.debug('Debug message');
            expect(captured.length).toBe(1);
            expect(captured[0]).toContain('DEBUG');
        });

        it('should log at info level', () => {
            log.info('Info message');
            expect(captured.length).toBe(1);
            expect(captured[0]).toContain('INFO');
        });

        it('should log at warn level', () => {
            log.warn('Warn message');
            expect(captured.length).toBe(1);
            expect(captured[0]).toContain('WARN');
        });

        it('should log at error level', () => {
            log.error('Error message');
            expect(captured.length).toBe(1);
            expect(captured[0]).toContain('ERROR');
        });

        it('should have log() as alias for info()', () => {
            log.log('Log message');
            expect(captured.length).toBe(1);
            expect(captured[0]).toContain('INFO');
        });
    });

    // =========================================================================
    // Log Formatting
    // =========================================================================

    describe('Log Formatting', () => {
        it('should include timestamp when enabled', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', {
                level: 'info',
                output,
                timestamp: true,
            });

            log.info('Test message');
            expect(captured[0]).toMatch(/\d{4}-\d{2}-\d{2}/);
        });

        it('should include package and filename', () => {
            const { captured, output } = createOutputCapture();
            const log = create('my-package', 'my-file.mjs', {
                level: 'info',
                output,
            });

            log.info('Test message');
            expect(captured[0]).toContain('my-package');
            expect(captured[0]).toContain('my-file.mjs');
        });

        it('should include data as JSON', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', { level: 'info', output });

            log.info('Test message', { key: 'value', num: 42 });
            expect(captured[0]).toContain('"key":"value"');
            expect(captured[0]).toContain('"num":42');
        });

        it('should output JSON format when configured', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', {
                level: 'info',
                output,
                json: true,
            });

            log.info('Test message');
            const parsed = JSON.parse(captured[0]);
            expect(parsed.message).toBe('Test message');
            expect(parsed.level).toBe('info');
        });
    });

    // =========================================================================
    // Child Logger
    // =========================================================================

    describe('Child Logger', () => {
        it('should create child with same package', () => {
            const parent = create('parent-package', 'parent.mjs');
            const child = parent.child('child.mjs');

            expect(child.packageName).toBe('parent-package');
            expect(child.filename).toBe('child.mjs');
        });

        it('should allow config overrides in child', () => {
            const parent = create('parent', 'parent.mjs', { level: 'info' });
            const child = parent.child('child.mjs', { level: 'debug' });

            expect(child.level).toBe('debug');
        });
    });

    // =========================================================================
    // Context Logger
    // =========================================================================

    describe('Context Logger', () => {
        it('should create logger with context', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', { level: 'info', output });
            const ctxLog = log.withContext({ requestId: '123' });

            ctxLog.info('Test message');
            expect(captured[0]).toContain('requestId');
            expect(captured[0]).toContain('123');
        });

        it('should merge context with additional data', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', { level: 'info', output });
            const ctxLog = log.withContext({ requestId: '123' });

            ctxLog.info('Test message', { extra: 'data' });
            expect(captured[0]).toContain('requestId');
            expect(captured[0]).toContain('extra');
        });

        it('should have all log methods', () => {
            const log = create('test', 'test.mjs');
            const ctxLog = log.withContext({ ctx: 'value' });

            expect(typeof ctxLog.log).toBe('function');
            expect(typeof ctxLog.info).toBe('function');
            expect(typeof ctxLog.warn).toBe('function');
            expect(typeof ctxLog.error).toBe('function');
            expect(typeof ctxLog.debug).toBe('function');
            expect(typeof ctxLog.trace).toBe('function');
        });
    });

    // =========================================================================
    // LOG_LEVELS Constant
    // =========================================================================

    describe('LOG_LEVELS', () => {
        it('should have error as lowest priority', () => {
            expect(LOG_LEVELS.error).toBe(0);
        });

        it('should have warn priority 1', () => {
            expect(LOG_LEVELS.warn).toBe(1);
        });

        it('should have info priority 2', () => {
            expect(LOG_LEVELS.info).toBe(2);
        });

        it('should have debug priority 3', () => {
            expect(LOG_LEVELS.debug).toBe(3);
        });

        it('should have trace as highest priority', () => {
            expect(LOG_LEVELS.trace).toBe(4);
        });
    });

    // =========================================================================
    // Error Handling
    // =========================================================================

    describe('Error Handling', () => {
        it('should include error stack in output', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', { level: 'error', output });

            const error = new Error('Test error');
            log.error('Error occurred', error);

            expect(captured[0]).toContain('Error');
            expect(captured[0]).toContain('Test error');
        });

        it('should serialize error in JSON format', () => {
            const { captured, output } = createOutputCapture();
            const log = create('test', 'test.mjs', {
                level: 'error',
                output,
                json: true,
            });

            const error = new Error('Test error');
            log.error('Error occurred', error);

            const parsed = JSON.parse(captured[0]);
            expect(parsed.error).toBeDefined();
            expect(parsed.error.message).toBe('Test error');
            expect(parsed.error.name).toBe('Error');
        });
    });

    // =========================================================================
    // Default Config
    // =========================================================================

    describe('Default Config', () => {
        it('should expose DEFAULT_CONFIG', () => {
            expect(logger.DEFAULT_CONFIG).toBeDefined();
            expect(logger.DEFAULT_CONFIG.level).toBeDefined();
        });

        it('should use info as default level', () => {
            // Save original env
            const originalLevel = process.env.LOG_LEVEL;
            delete process.env.LOG_LEVEL;

            const log = create('test', 'test.mjs');
            expect(log.level).toBe('info');

            // Restore
            if (originalLevel) process.env.LOG_LEVEL = originalLevel;
        });
    });
});
