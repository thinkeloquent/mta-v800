/**
 * Mock Logger for test verification.
 *
 * Following FORMAT_TEST.yaml specification for:
 * - Log verification (hyper-observability)
 * - Mock logger injection
 */
import { ILogger } from '../../src/logger.js';

interface LogEntry {
    msg: string;
    args: any[];
}

interface LogCollection {
    trace: LogEntry[];
    debug: LogEntry[];
    info: LogEntry[];
    warn: LogEntry[];
    error: LogEntry[];
}

export class MockLogger implements ILogger {
    public logs: LogCollection;

    constructor() {
        this.logs = {
            trace: [],
            debug: [],
            info: [],
            warn: [],
            error: []
        };
    }

    trace(msg: string, ...args: any[]): void {
        this.logs.trace.push({ msg, args });
    }

    debug(msg: string, ...args: any[]): void {
        this.logs.debug.push({ msg, args });
    }

    info(msg: string, ...args: any[]): void {
        this.logs.info.push({ msg, args });
    }

    warn(msg: string, ...args: any[]): void {
        this.logs.warn.push({ msg, args });
    }

    error(msg: string, ...args: any[]): void {
        this.logs.error.push({ msg, args });
    }

    contains(level: keyof LogCollection, text: string): boolean {
        return this.logs[level].some(entry => entry.msg.includes(text));
    }

    allMessages(): string[] {
        const messages: string[] = [];
        for (const [level, entries] of Object.entries(this.logs)) {
            for (const entry of entries) {
                messages.push(`[${level.toUpperCase()}] ${entry.msg}`);
            }
        }
        return messages;
    }

    clear(): void {
        this.logs = {
            trace: [],
            debug: [],
            info: [],
            warn: [],
            error: []
        };
    }
}

export function createMockLogger(): MockLogger {
    return new MockLogger();
}
