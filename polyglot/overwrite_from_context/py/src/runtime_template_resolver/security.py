import re
from typing import Set

from .errors import SecurityError, ErrorCode

class Security:
    # Allowed: start with alpha, then alpha/num/underscore/dot
    # This automatically blocks leading underscore/numeric, except underscore inside is allowed.
    # But wait, leading underscore is blocked by ^[a-zA-Z]
    PATH_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_.]*$')
    
    BLOCKED_PATTERNS = {
        "__proto__",
        "__class__",
        "__dict__",
        "constructor",
        "prototype"
    }

    @classmethod
    def validate_path(cls, path: str) -> None:
        if not path:
             raise SecurityError("Path cannot be empty", ErrorCode.SECURITY_BLOCKED_PATH)

        if not cls.PATH_PATTERN.match(path):
            raise SecurityError(
                f"Invalid path: {path}. Must start with letter and contain only alphanumeric, underscore, or dot.",
                ErrorCode.SECURITY_BLOCKED_PATH,
                {"path": path}
            )

        # Check for blocked segments logic could be here if regex wasn't restrictive enough,
        # but regex ensures it starts with a letter.
        # However, we should still check specifically for blocked words if they appear as segments?
        # E.g. "a.constructor.b"
        
        segments = path.split('.')
        for segment in segments:
             if segment in cls.BLOCKED_PATTERNS:
                 raise SecurityError(
                     f"Path contains blocked segment: {segment}",
                     ErrorCode.SECURITY_BLOCKED_PATH,
                     {"path": path, "segment": segment}
                 )
             if segment.startswith("_"):
                 # Redundant with regex for first segment, but good for subsequent segments if regex allowed them.
                 # Actually regex ^[a-zA-Z][...]* matches THE WHOLE STRING.
                 # So "a._b" matches the regex? Yes, "a" is alpha, "." is allowed, "_" is allowed.
                 # So we MUST check segments for underscore prefix if we want to block "_internal" in nested props?
                 # Plan says: "Block underscore prefix: _private, _internal"
                 # And "Allowed path pattern: ^[a-zA-Z][a-zA-Z0-9_.]*$"
                 # If "user._private" is allowed by regex, but we want to block it?
                 # Feature 4.1 says "Block underscore prefix". Usually applies to any segment.
                 raise SecurityError(
                     f"Path segment starts with underscore: {segment}",
                     ErrorCode.SECURITY_BLOCKED_PATH,
                     {"path": path, "segment": segment}
                 )
             if ".." in segment: # Should be impossible if split by dot, unless path has ".." inside and we split.
                 # If path is "a..b", split gives ["a", "", "b"]. Empty string.
                 pass
        
        if ".." in path:
             # Logic for ".."
             # Regex prevents ".." if we don't assume dots are separators in the regex?
             # Regex `[a-zA-Z0-9_.]*` allows `..`.
             raise SecurityError(
                 "Path traversal not allowed (..)",
                 ErrorCode.SECURITY_BLOCKED_PATH,
                 {"path": path}
             )

