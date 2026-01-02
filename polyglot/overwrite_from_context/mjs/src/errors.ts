export enum ErrorCode {
    COMPUTE_FUNCTION_NOT_FOUND = 'ERR_COMPUTE_NOT_FOUND',
    COMPUTE_FUNCTION_FAILED = 'ERR_COMPUTE_FAILED',
    SECURITY_BLOCKED_PATH = 'ERR_SECURITY_PATH',
    RECURSION_LIMIT = 'ERR_RECURSION_LIMIT',
    SCOPE_VIOLATION = 'ERR_SCOPE_VIOLATION',
    VALIDATION_ERROR = 'ERR_VALIDATION_ERROR'
}

export class ResolveError extends Error {
    code: string;
    context: Record<string, any>;

    constructor(message: string, code: string, context?: Record<string, any>) {
        super(message);
        this.name = this.constructor.name;
        this.code = code;
        this.context = context || {};
    }
}

export class ComputeFunctionError extends ResolveError { }
export class SecurityError extends ResolveError { }
export class RecursionLimitError extends ResolveError { }
export class ScopeViolationError extends ResolveError { }
export class ValidationError extends ResolveError { }
