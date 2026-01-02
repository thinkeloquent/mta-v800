class ErrorCode:
    COMPUTE_FUNCTION_NOT_FOUND = "ERR_COMPUTE_NOT_FOUND"
    COMPUTE_FUNCTION_FAILED = "ERR_COMPUTE_FAILED"
    SECURITY_BLOCKED_PATH = "ERR_SECURITY_PATH"
    RECURSION_LIMIT = "ERR_RECURSION_LIMIT"
    SCOPE_VIOLATION = "ERR_SCOPE_VIOLATION"
    VALIDATION_ERROR = "ERR_VALIDATION_ERROR"

class ResolveError(Exception):
    """Base class for resolver errors"""
    def __init__(self, message: str, code: str, context: dict = None):
        super().__init__(message)
        self.code = code
        self.context = context or {}

class ComputeFunctionError(ResolveError):
    pass

class SecurityError(ResolveError):
    pass

class RecursionLimitError(ResolveError):
    pass

class ScopeViolationError(ResolveError):
    pass

class ValidationError(ResolveError):
    pass
