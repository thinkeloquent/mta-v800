export enum ComputeScope {
    STARTUP = 'STARTUP',
    REQUEST = 'REQUEST'
}

export enum MissingStrategy {
    ERROR = 'ERROR',
    DEFAULT = 'DEFAULT',
    IGNORE = 'IGNORE'
}

export interface ResolverOptions {
    logger?: any;
    maxDepth?: number;
    missingStrategy?: MissingStrategy;
}
