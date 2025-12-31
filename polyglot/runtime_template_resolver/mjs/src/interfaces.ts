import { LoggerInterface } from './logger.js';

export enum MissingStrategy {
    KEEP = 'KEEP',
    EMPTY = 'EMPTY',
    ERROR = 'ERROR',
    DEFAULT = 'DEFAULT',
}

export interface IResolverOptions {
    missingStrategy?: MissingStrategy;
    throwOnError?: boolean;
    logger?: LoggerInterface;
}

export interface IResolverResult {
    value: string;
    placeholders: string[];
    errors: Error[];
}

export interface ITemplateResolver {
    resolve(template: string, context: Record<string, unknown>, options?: IResolverOptions): string;
    resolveObject(obj: unknown, context: Record<string, unknown>, options?: IResolverOptions): unknown;
}
