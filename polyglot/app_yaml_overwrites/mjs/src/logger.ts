
export class Logger {
    private package: string;
    private filename: string;
    private level: string;

    constructor(packageName: string, filename: string) {
        this.package = packageName;
        this.filename = filename;
        this.level = process.env.LOG_LEVEL?.toLowerCase() || 'debug';
    }

    static create(packageName: string, filename: string): Logger {
        return new Logger(packageName, filename);
    }

    debug(message: string, data?: Record<string, any>): void {
        if (this.shouldLog('debug')) {
            console.log(JSON.stringify({
                timestamp: new Date().toISOString(),
                level: 'DEBUG',
                context: `${this.package}:${this.filename}`,
                message,
                data
            }));
        }
    }

    info(message: string, data?: Record<string, any>): void {
        if (this.shouldLog('info')) {
            console.log(JSON.stringify({
                timestamp: new Date().toISOString(),
                level: 'INFO',
                context: `${this.package}:${this.filename}`,
                message,
                data
            }));
        }
    }

    warn(message: string, data?: Record<string, any>): void {
        if (this.shouldLog('warn')) {
            console.log(JSON.stringify({
                timestamp: new Date().toISOString(),
                level: 'WARN',
                context: `${this.package}:${this.filename}`,
                message,
                data
            }));
        }
    }

    error(message: string, data?: Record<string, any>): void {
        if (this.shouldLog('error')) {
            console.error(JSON.stringify({
                timestamp: new Date().toISOString(),
                level: 'ERROR',
                context: `${this.package}:${this.filename}`,
                message,
                data
            }));
        }
    }

    private shouldLog(level: string): boolean {
        const levels = ['trace', 'debug', 'info', 'warn', 'error'];
        const currentLevelIdx = levels.indexOf(this.level);
        const msgLevelIdx = levels.indexOf(level);
        // If invalid level setup, default to allowing INFO+
        if (currentLevelIdx === -1) return levels.indexOf('info') <= msgLevelIdx;
        return currentLevelIdx <= msgLevelIdx;
    }
}
