/**
 * Unit tests for vault_file logger module.
 *
 * Tests cover:
 * - Statement coverage for all code paths
 * - Branch coverage for all conditionals
 * - Boundary value analysis
 */
import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { Logger, LogLevel, setLogLevel, getLogger } from '../src/logger';
describe('Logger Module', () => {
    // Store original console methods
    const originalConsole = {
        debug: console.debug,
        info: console.info,
        warn: console.warn,
        error: console.error,
    };
    // Mock console methods
    let mockDebug;
    let mockInfo;
    let mockWarn;
    let mockError;
    beforeEach(() => {
        mockDebug = jest.fn();
        mockInfo = jest.fn();
        mockWarn = jest.fn();
        mockError = jest.fn();
        console.debug = mockDebug;
        console.info = mockInfo;
        console.warn = mockWarn;
        console.error = mockError;
        // Reset log level to INFO
        setLogLevel(LogLevel.INFO);
    });
    afterEach(() => {
        // Restore original console methods
        console.debug = originalConsole.debug;
        console.info = originalConsole.info;
        console.warn = originalConsole.warn;
        console.error = originalConsole.error;
    });
    // =========================================================================
    // Logger Class Tests
    // =========================================================================
    describe('Logger', () => {
        describe('Statement Coverage', () => {
            it('should create logger instance via static create()', () => {
                const logger = Logger.create('test_package', 'test_file');
                expect(logger).toBeDefined();
            });
            it('should format context in messages', () => {
                setLogLevel(LogLevel.INFO);
                const logger = Logger.create('my_package', 'my_file');
                logger.info('test message');
                expect(mockInfo).toHaveBeenCalled();
                const call = mockInfo.mock.calls[0][0];
                expect(call).toContain('[my_package:my_file]');
                expect(call).toContain('test message');
            });
        });
        describe('Branch Coverage', () => {
            it('should log debug at DEBUG level', () => {
                setLogLevel(LogLevel.DEBUG);
                const logger = Logger.create('test', 'debug_test');
                logger.debug('debug message');
                expect(mockDebug).toHaveBeenCalled();
                expect(mockDebug.mock.calls[0][0]).toContain('debug message');
            });
            it('should not log debug at INFO level', () => {
                setLogLevel(LogLevel.INFO);
                const logger = Logger.create('test', 'info_test');
                logger.debug('should not appear');
                expect(mockDebug).not.toHaveBeenCalled();
            });
            it('should log info at INFO level', () => {
                setLogLevel(LogLevel.INFO);
                const logger = Logger.create('test', 'info_test');
                logger.info('info message');
                expect(mockInfo).toHaveBeenCalled();
                expect(mockInfo.mock.calls[0][0]).toContain('info message');
            });
            it('should log warn at WARN level', () => {
                setLogLevel(LogLevel.WARN);
                const logger = Logger.create('test', 'warn_test');
                logger.warn('warn message');
                expect(mockWarn).toHaveBeenCalled();
                expect(mockWarn.mock.calls[0][0]).toContain('warn message');
            });
            it('should log error at ERROR level', () => {
                setLogLevel(LogLevel.ERROR);
                const logger = Logger.create('test', 'error_test');
                logger.error('error message');
                expect(mockError).toHaveBeenCalled();
                expect(mockError.mock.calls[0][0]).toContain('error message');
            });
            it('should not log anything at NONE level', () => {
                setLogLevel(LogLevel.NONE);
                const logger = Logger.create('test', 'none_test');
                logger.debug('debug');
                logger.info('info');
                logger.warn('warn');
                logger.error('error');
                expect(mockDebug).not.toHaveBeenCalled();
                expect(mockInfo).not.toHaveBeenCalled();
                expect(mockWarn).not.toHaveBeenCalled();
                expect(mockError).not.toHaveBeenCalled();
            });
        });
        describe('Log Level Filtering', () => {
            it('should log info and above at INFO level', () => {
                setLogLevel(LogLevel.INFO);
                const logger = Logger.create('test', 'test');
                logger.debug('debug');
                logger.info('info');
                logger.warn('warn');
                logger.error('error');
                expect(mockDebug).not.toHaveBeenCalled();
                expect(mockInfo).toHaveBeenCalled();
                expect(mockWarn).toHaveBeenCalled();
                expect(mockError).toHaveBeenCalled();
            });
            it('should log warn and above at WARN level', () => {
                setLogLevel(LogLevel.WARN);
                const logger = Logger.create('test', 'test');
                logger.debug('debug');
                logger.info('info');
                logger.warn('warn');
                logger.error('error');
                expect(mockDebug).not.toHaveBeenCalled();
                expect(mockInfo).not.toHaveBeenCalled();
                expect(mockWarn).toHaveBeenCalled();
                expect(mockError).toHaveBeenCalled();
            });
            it('should log only error at ERROR level', () => {
                setLogLevel(LogLevel.ERROR);
                const logger = Logger.create('test', 'test');
                logger.debug('debug');
                logger.info('info');
                logger.warn('warn');
                logger.error('error');
                expect(mockDebug).not.toHaveBeenCalled();
                expect(mockInfo).not.toHaveBeenCalled();
                expect(mockWarn).not.toHaveBeenCalled();
                expect(mockError).toHaveBeenCalled();
            });
        });
    });
    // =========================================================================
    // LogLevel Enum Tests
    // =========================================================================
    describe('LogLevel', () => {
        describe('Statement Coverage', () => {
            it('should have DEBUG value 0', () => {
                expect(LogLevel.DEBUG).toBe(0);
            });
            it('should have INFO value 1', () => {
                expect(LogLevel.INFO).toBe(1);
            });
            it('should have WARN value 2', () => {
                expect(LogLevel.WARN).toBe(2);
            });
            it('should have ERROR value 3', () => {
                expect(LogLevel.ERROR).toBe(3);
            });
            it('should have NONE value 4', () => {
                expect(LogLevel.NONE).toBe(4);
            });
        });
        describe('Comparison', () => {
            it('should compare DEBUG < INFO', () => {
                expect(LogLevel.DEBUG).toBeLessThan(LogLevel.INFO);
            });
            it('should compare INFO < WARN', () => {
                expect(LogLevel.INFO).toBeLessThan(LogLevel.WARN);
            });
            it('should compare WARN < ERROR', () => {
                expect(LogLevel.WARN).toBeLessThan(LogLevel.ERROR);
            });
            it('should compare ERROR < NONE', () => {
                expect(LogLevel.ERROR).toBeLessThan(LogLevel.NONE);
            });
        });
    });
    // =========================================================================
    // setLogLevel Function Tests
    // =========================================================================
    describe('setLogLevel()', () => {
        it('should enable all logs at DEBUG level', () => {
            setLogLevel(LogLevel.DEBUG);
            const logger = Logger.create('test', 'test');
            logger.debug('debug');
            expect(mockDebug).toHaveBeenCalled();
        });
        it('should disable all logs at NONE level', () => {
            setLogLevel(LogLevel.NONE);
            const logger = Logger.create('test', 'test');
            logger.error('error');
            expect(mockError).not.toHaveBeenCalled();
        });
    });
    // =========================================================================
    // getLogger Function Tests
    // =========================================================================
    describe('getLogger()', () => {
        it('should return default logger', () => {
            const logger = getLogger();
            expect(logger).toBeDefined();
        });
        it('should return same instance on multiple calls', () => {
            const logger1 = getLogger();
            const logger2 = getLogger();
            expect(logger1).toBe(logger2);
        });
    });
    // =========================================================================
    // IVaultFileLogger Interface Tests
    // =========================================================================
    describe('IVaultFileLogger Interface', () => {
        it('should implement debug method', () => {
            const logger = Logger.create('test', 'test');
            expect(typeof logger.debug).toBe('function');
        });
        it('should implement info method', () => {
            const logger = Logger.create('test', 'test');
            expect(typeof logger.info).toBe('function');
        });
        it('should implement warn method', () => {
            const logger = Logger.create('test', 'test');
            expect(typeof logger.warn).toBe('function');
        });
        it('should implement error method', () => {
            const logger = Logger.create('test', 'test');
            expect(typeof logger.error).toBe('function');
        });
    });
});
//# sourceMappingURL=logger.test.js.map