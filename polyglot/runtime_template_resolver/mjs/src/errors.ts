export class SecurityError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'SecurityError';
    }
}

export class ValidationError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'ValidationError';
    }
}

export class MissingValueError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'MissingValueError';
    }
}
