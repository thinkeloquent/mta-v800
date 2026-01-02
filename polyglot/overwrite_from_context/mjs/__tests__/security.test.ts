/**
 * Unit tests for Security module.
 *
 * Tests cover:
 * - Path validation
 * - Blocked pattern detection
 * - Underscore prefix blocking
 * - Path traversal blocking
 *
 * Following FORMAT_TEST.yaml specification.
 */
import { describe, it, expect } from 'vitest';
import { Security } from '../src/security.js';
import { SecurityError, ErrorCode } from '../src/errors.js';

describe('Security', () => {

    // =========================================================================
    // Statement Coverage
    // =========================================================================

    describe('StatementCoverage', () => {
        it('should pass validation for valid paths', () => {
            expect(() => Security.validatePath('database.host')).not.toThrow();
            expect(() => Security.validatePath('app')).not.toThrow();
            expect(() => Security.validatePath('config.server.port')).not.toThrow();
            expect(() => Security.validatePath('a1.b2.c3')).not.toThrow();
        });

        it('should pass validation for single segment path', () => {
            expect(() => Security.validatePath('hostname')).not.toThrow();
        });
    });

    // =========================================================================
    // Branch Coverage
    // =========================================================================

    describe('BranchCoverage', () => {
        it('should throw for empty path', () => {
            expect(() => Security.validatePath('')).toThrow(SecurityError);

            try {
                Security.validatePath('');
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.SECURITY_BLOCKED_PATH);
                expect(e.message.toLowerCase()).toContain('empty');
            }
        });

        it('should throw for path starting with number', () => {
            expect(() => Security.validatePath('123invalid')).toThrow(SecurityError);

            try {
                Security.validatePath('123invalid');
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.SECURITY_BLOCKED_PATH);
            }
        });

        it('should throw for path starting with underscore', () => {
            expect(() => Security.validatePath('_private')).toThrow(SecurityError);

            try {
                Security.validatePath('_private');
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.SECURITY_BLOCKED_PATH);
            }
        });

        it('should throw for path with underscore prefix in segment', () => {
            expect(() => Security.validatePath('valid._internal')).toThrow(SecurityError);

            try {
                Security.validatePath('valid._internal');
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.SECURITY_BLOCKED_PATH);
                expect(e.message).toContain('_internal');
            }
        });
    });

    // =========================================================================
    // Boundary Value Analysis
    // =========================================================================

    describe('BoundaryValueAnalysis', () => {
        it('should block __proto__', () => {
            expect(() => Security.validatePath('obj.__proto__')).toThrow(SecurityError);

            try {
                Security.validatePath('obj.__proto__');
            } catch (e: any) {
                expect(e.message).toContain('__proto__');
            }
        });

        it('should block __class__', () => {
            expect(() => Security.validatePath('obj.__class__')).toThrow(SecurityError);

            try {
                Security.validatePath('obj.__class__');
            } catch (e: any) {
                expect(e.message).toContain('__class__');
            }
        });

        it('should block __dict__', () => {
            expect(() => Security.validatePath('obj.__dict__')).toThrow(SecurityError);

            try {
                Security.validatePath('obj.__dict__');
            } catch (e: any) {
                expect(e.message).toContain('__dict__');
            }
        });

        it('should block constructor', () => {
            expect(() => Security.validatePath('obj.constructor')).toThrow(SecurityError);

            try {
                Security.validatePath('obj.constructor');
            } catch (e: any) {
                expect(e.message).toContain('constructor');
            }
        });

        it('should block prototype', () => {
            expect(() => Security.validatePath('obj.prototype')).toThrow(SecurityError);

            try {
                Security.validatePath('obj.prototype');
            } catch (e: any) {
                expect(e.message).toContain('prototype');
            }
        });

        it('should block path traversal (..)', () => {
            expect(() => Security.validatePath('a..b')).toThrow(SecurityError);

            try {
                Security.validatePath('a..b');
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.SECURITY_BLOCKED_PATH);
                expect(e.message).toContain('..');
            }
        });

        it('should block special characters', () => {
            const invalidPaths = [
                'path-with-dash',
                'path with space',
                'path/with/slash',
                'path\\with\\backslash',
                'path@symbol',
                'path$dollar'
            ];

            for (const path of invalidPaths) {
                expect(() => Security.validatePath(path)).toThrow(SecurityError);
            }
        });
    });

    // =========================================================================
    // Error Handling
    // =========================================================================

    describe('ErrorHandling', () => {
        it('should include path in SecurityError context', () => {
            try {
                Security.validatePath('bad.constructor.access');
            } catch (e: any) {
                expect(e.code).toBe(ErrorCode.SECURITY_BLOCKED_PATH);
                expect(e.context).toBeDefined();
            }
        });

        it('should detect blocked pattern in nested path', () => {
            expect(() => Security.validatePath('deeply.nested.__proto__.path')).toThrow(SecurityError);
        });
    });

    // =========================================================================
    // Integration Tests
    // =========================================================================

    describe('Integration', () => {
        it('should pass realistic config paths', () => {
            const validPaths = [
                'database.host',
                'database.port',
                'server.http.port',
                'app.name',
                'providers.aws.region',
                'services.api.timeout',
                'env.NODE_ENV',
                'secrets.apiKey'
            ];

            for (const path of validPaths) {
                expect(() => Security.validatePath(path)).not.toThrow();
            }
        });

        it('should block common attack vectors', () => {
            const attackPaths = [
                '__proto__',
                'constructor.prototype',
                'a.__proto__.polluted',
                '_private_data',
                'user._password'
            ];

            for (const path of attackPaths) {
                expect(() => Security.validatePath(path)).toThrow(SecurityError);
            }
        });
    });
});
