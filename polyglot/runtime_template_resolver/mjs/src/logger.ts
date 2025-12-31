/**
 * Polyglot Logger Implementation
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LoggerInterface {
    debug(message: string, context?: Record<string, unknown>): void;
    info(message: string, context?: Record<string, unknown>): void;
    warn(message: string, context?: Record<string, unknown>): void;
    error(message: string, context?: Record<string, unknown>): void;
}

const LOG_LEVELS: Record<LogLevel, number> = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3,
};

class ConsoleLogger implements LoggerInterface {
    private packageName: string;
    private filename: string;
    private level: number;

    constructor(packageName: string, filename: string, level: LogLevel = 'debug') {
        this.packageName = packageName;
        this.filename = filename;
        this.level = LOG_LEVELS[level];
    }

    private shouldLog(level: LogLevel): boolean {
        return LOG_LEVELS[level] >= this.level;
    }

    private format(level: LogLevel, message: string, context?: Record<string, unknown>): void {
        if (!this.shouldLog(level)) return;

        // In node, filename might be full path, we want basename
        const plainFilename = this.filename.split(/[/\\]/).pop() || this.filename;
        const timestamp = new Date().toISOString();

        // Structured log format
        const output = {
            timestamp,
            level,
            package: this.packageName,
            file: plainFilename,
            message,
            ...context
        };

        console.log(JSON.stringify(output));
    }

    debug(message: string, context?: Record<string, unknown>): void {
        this.format('debug', message, context);
    }

    info(message: string, context?: Record<string, unknown>): void {
        this.format('info', message, context);
    }

    warn(message: string, context?: Record<string, unknown>): void {
        this.format('warn', message, context);
    }

    error(message: string, context?: Record<string, unknown>): void {
        this.format('error', message, context);
    }
}

export const logger = {
    create: (packageName: string, filename: string): LoggerInterface => {
        const envLevel = (process.env.LOG_LEVEL as LogLevel) || 'debug';
        return new ConsoleLogger(packageName, filename, envLevel);
    }
};
