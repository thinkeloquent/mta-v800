export class ConfigurationError extends Error {
    constructor(message: string, public context?: unknown) {
        super(`${message} (context: ${JSON.stringify(context)})`);
        this.name = 'ConfigurationError';
    }
}

export class ImmutabilityError extends ConfigurationError {
    constructor(message: string, context?: unknown) {
        super(message, context);
        this.name = 'ImmutabilityError';
    }
}

export function validateConfigKey(key: string): void {
    if (!key) {
        throw new ConfigurationError("Config key cannot be empty");
    }
}
