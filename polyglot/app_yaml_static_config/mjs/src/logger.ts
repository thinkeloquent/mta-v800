export interface ILogger {
    info(message: string, ...args: unknown[]): void;
    warn(message: string, ...args: unknown[]): void;
    error(message: string, ...args: unknown[]): void;
    debug(message: string, ...args: unknown[]): void;
    trace(message: string, ...args: unknown[]): void;
}

export function create(packageName: string, filename: string): ILogger {
    const prefix = `[${packageName}:${filename}]`;
    return {
        info: (msg, ...args) => console.info(`${prefix} INFO:`, msg, ...args),
        warn: (msg, ...args) => console.warn(`${prefix} WARN:`, msg, ...args),
        error: (msg, ...args) => console.error(`${prefix} ERROR:`, msg, ...args),
        debug: (msg, ...args) => console.debug(`${prefix} DEBUG:`, msg, ...args),
        trace: (msg, ...args) => console.trace(`${prefix} TRACE:`, msg, ...args),
    };
}
