from typing import Protocol, Any, Dict, List, Optional, Union

class ILogger(Protocol):
    def info(self, message: str, *args: Any) -> None: ...
    def warn(self, message: str, *args: Any) -> None: ...
    def error(self, message: str, *args: Any) -> None: ...
    def debug(self, message: str, *args: Any) -> None: ...
    def trace(self, message: str, *args: Any) -> None: ...

class InitOptions:
    def __init__(self,
                 files: List[str],
                 config_dir: str,
                 app_env: Optional[str] = None,
                 logger: Optional[ILogger] = None):
        self.files = files
        self.config_dir = config_dir
        self.app_env = app_env
        self.logger = logger
