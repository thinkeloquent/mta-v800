import { ILogger } from './logger.js';

export { ILogger };

export interface InitOptions {
    files: string[];
    configDir: string;
    appEnv?: string;
    logger?: ILogger;
}

export interface LoadResult {
    filesLoaded: string[];
}
