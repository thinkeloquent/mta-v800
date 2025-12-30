export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3,
    NONE = 4
}

let currentLevel = LogLevel.INFO;

export interface IVaultFileLogger {
    debug(message: string, ...args: any[]): void;
    info(message: string, ...args: any[]): void;
    warn(message: string, ...args: any[]): void;
    error(message: string, ...args: any[]): void;
}

export class Logger implements IVaultFileLogger {
    private context: string;

    private constructor(packageName: string, fileName: string) {
        this.context = `[${packageName}:${fileName}]`;
    }

    public static create(packageName: string, fileName: string): IVaultFileLogger {
        return new Logger(packageName, fileName);
    }

    private format(message: string): string {
        return `${this.context} ${message}`;
    }

    debug(message: string, ...args: any[]) {
        if (currentLevel <= LogLevel.DEBUG) console.debug(`[DEBUG] ${this.format(message)}`, ...args);
    }
    info(message: string, ...args: any[]) {
        if (currentLevel <= LogLevel.INFO) console.info(`[INFO] ${this.format(message)}`, ...args);
    }
    warn(message: string, ...args: any[]) {
        if (currentLevel <= LogLevel.WARN) console.warn(`[WARN] ${this.format(message)}`, ...args);
    }
    error(message: string, ...args: any[]) {
        if (currentLevel <= LogLevel.ERROR) console.error(`[ERROR] ${this.format(message)}`, ...args);
    }
}

// Default singleton for backward compatibility if needed, though 'create' is preferred
const defaultLogger = Logger.create('vault-file', 'default');

export function getLogger(): IVaultFileLogger {
    return defaultLogger;
}

export function setLogLevel(level: LogLevel) {
    currentLevel = level;
}

