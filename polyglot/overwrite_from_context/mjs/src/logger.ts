
import path from 'path';

export enum LogLevel {
    TRACE = 5,
    DEBUG = 10,
    INFO = 20,
    WARN = 30,
    ERROR = 40,
    SILENT = 100
}

const DEFAULT_LOG_LEVEL = LogLevel.DEBUG;

export interface ILogger {
    trace(msg: string, ...args: any[]): void;
    debug(msg: string, ...args: any[]): void;
    info(msg: string, ...args: any[]): void;
    warn(msg: string, ...args: any[]): void;
    error(msg: string, ...args: any[]): void;
}

export class Logger implements ILogger {
    private package: string;
    private filename: string;
    private level: LogLevel;
    private prefix: string;

    private constructor(packageName: string, filename: string, level?: LogLevel) {
        this.package = packageName;
        this.filename = path.basename(filename);
        this.level = level !== undefined ? level : Logger.getEnvLevel();
        this.prefix = `[${this.package}:${this.filename}]`;
    }

    private static getEnvLevel(): LogLevel {
        const envLevel = (process.env.LOG_LEVEL || 'debug').toUpperCase();
        if (envLevel in LogLevel) {
            return LogLevel[envLevel as keyof typeof LogLevel];
        }
        return DEFAULT_LOG_LEVEL;
    }

    public static create(packageName: string, filename: string, level?: LogLevel): Logger {
        return new Logger(packageName, filename, level);
    }

    private log(level: LogLevel, levelName: string, msg: string, ...args: any[]): void {
        if (this.level <= level) {
            const method = level >= LogLevel.ERROR ? console.error : console.log;
            method(`${this.prefix} ${levelName}: ${msg}`, ...args);
        }
    }

    public trace(msg: string, ...args: any[]): void {
        this.log(LogLevel.TRACE, 'TRACE', msg, ...args);
    }

    public debug(msg: string, ...args: any[]): void {
        this.log(LogLevel.DEBUG, 'DEBUG', msg, ...args);
    }

    public info(msg: string, ...args: any[]): void {
        this.log(LogLevel.INFO, 'INFO', msg, ...args);
    }

    public warn(msg: string, ...args: any[]): void {
        this.log(LogLevel.WARN, 'WARN', msg, ...args);
    }

    public error(msg: string, ...args: any[]): void {
        this.log(LogLevel.ERROR, 'ERROR', msg, ...args);
    }
}
