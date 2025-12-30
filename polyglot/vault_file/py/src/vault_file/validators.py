class EnvKeyNotFoundError(Exception):
    def __init__(self, key: str):
        self.key = key
        super().__init__(f"Environment variable '{key}' not found")
