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

class ConsoleLogger implements IVaultFileLogger {
    debug(message: string, ...args: any[]) {
        if (currentLevel <= LogLevel.DEBUG) console.debug(`[DEBUG] ${message}`, ...args);
    }
    info(message: string, ...args: any[]) {
        if (currentLevel <= LogLevel.INFO) console.info(`[INFO] ${message}`, ...args);
    }
    warn(message: string, ...args: any[]) {
        if (currentLevel <= LogLevel.WARN) console.warn(`[WARN] ${message}`, ...args);
    }
    error(message: string, ...args: any[]) {
        if (currentLevel <= LogLevel.ERROR) console.error(`[ERROR] ${message}`, ...args);
    }
}

const logger = new ConsoleLogger();

export function getLogger(): IVaultFileLogger {
    return logger;
}

export function setLogLevel(level: LogLevel) {
    currentLevel = level;
}
