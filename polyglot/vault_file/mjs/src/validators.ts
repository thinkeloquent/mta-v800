export class EnvKeyNotFoundError extends Error {
  constructor(key: string) {
    super(`Environment variable not found: ${key}`);
    this.name = 'EnvKeyNotFoundError';
  }
}
