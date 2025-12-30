/**
 * Unit tests for app-yaml-static-config logger module.
 *
 * Tests cover:
 * - Logger factory function
 * - Logger method calls
 * - Prefix formatting
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { create } from '../dist/logger.js';

describe('Logger', () => {
    let consoleInfoSpy;
    let consoleWarnSpy;
    let consoleErrorSpy;
    let consoleDebugSpy;
    let consoleTraceSpy;

    beforeEach(() => {
        consoleInfoSpy = vi.spyOn(console, 'info').mockImplementation(() => {});
        consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
        consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
        consoleDebugSpy = vi.spyOn(console, 'debug').mockImplementation(() => {});
        consoleTraceSpy = vi.spyOn(console, 'trace').mockImplementation(() => {});
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    describe('Statement Coverage', () => {
        it('should create logger instance with all methods', () => {
            const logger = create('test_package', 'test_file.ts');

            expect(logger).toBeDefined();
            expect(typeof logger.info).toBe('function');
            expect(typeof logger.warn).toBe('function');
            expect(typeof logger.error).toBe('function');
            expect(typeof logger.debug).toBe('function');
            expect(typeof logger.trace).toBe('function');
        });

        it('should call console.info for info()', () => {
            const logger = create('test_package', 'test_file.ts');

            logger.info('Test info message');

            expect(consoleInfoSpy).toHaveBeenCalled();
            const call = consoleInfoSpy.mock.calls[0];
            expect(call[0]).toContain('[test_package:test_file.ts]');
            expect(call[0]).toContain('INFO');
        });

        it('should call console.warn for warn()', () => {
            const logger = create('test_package', 'test_file.ts');

            logger.warn('Test warn message');

            expect(consoleWarnSpy).toHaveBeenCalled();
            const call = consoleWarnSpy.mock.calls[0];
            expect(call[0]).toContain('WARN');
        });

        it('should call console.error for error()', () => {
            const logger = create('test_package', 'test_file.ts');

            logger.error('Test error message');

            expect(consoleErrorSpy).toHaveBeenCalled();
            const call = consoleErrorSpy.mock.calls[0];
            expect(call[0]).toContain('ERROR');
        });

        it('should call console.debug for debug()', () => {
            const logger = create('test_package', 'test_file.ts');

            logger.debug('Test debug message');

            expect(consoleDebugSpy).toHaveBeenCalled();
            const call = consoleDebugSpy.mock.calls[0];
            expect(call[0]).toContain('DEBUG');
        });

        it('should call console.trace for trace()', () => {
            const logger = create('test_package', 'test_file.ts');

            logger.trace('Test trace message');

            expect(consoleTraceSpy).toHaveBeenCalled();
            const call = consoleTraceSpy.mock.calls[0];
            expect(call[0]).toContain('TRACE');
        });
    });

    describe('Branch Coverage', () => {
        it('should include package name and filename in prefix', () => {
            const logger = create('my_package', 'my_file.ts');

            logger.info('Test message');

            const call = consoleInfoSpy.mock.calls[0];
            expect(call[0]).toContain('[my_package:my_file.ts]');
        });

        it('should pass additional arguments', () => {
            const logger = create('test_package', 'test_file.ts');

            logger.info('Message with args', { key: 'value' });

            expect(consoleInfoSpy).toHaveBeenCalledWith(
                expect.stringContaining('[test_package:test_file.ts]'),
                'Message with args',
                { key: 'value' }
            );
        });
    });

    describe('Integration', () => {
        it('should create independent logger instances', () => {
            const logger1 = create('package1', 'file1.ts');
            const logger2 = create('package2', 'file2.ts');

            logger1.info('Message 1');
            logger2.info('Message 2');

            expect(consoleInfoSpy).toHaveBeenCalledTimes(2);

            const call1 = consoleInfoSpy.mock.calls[0];
            const call2 = consoleInfoSpy.mock.calls[1];

            expect(call1[0]).toContain('[package1:file1.ts]');
            expect(call2[0]).toContain('[package2:file2.ts]');
        });
    });
});
