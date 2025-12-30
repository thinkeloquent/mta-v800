import fs from 'fs';
import path from 'path';
import { LoadResult } from './domain.js';
import { parseEnvFile } from './core.js';
import { EnvKeyNotFoundError } from './validators.js';
import { IVaultFileLogger, getLogger, Logger } from './logger.js';

export class EnvStore {
  private static instance: EnvStore;
  private store: Record<string, string> = {};
  private _initialized = false;
  private _totalVarsLoaded = 0;
  private logger: IVaultFileLogger;

  private constructor() {
    this.logger = getLogger();
  }

  public static getInstance(): EnvStore {
    if (!EnvStore.instance) {
      EnvStore.instance = new EnvStore();
    }
    return EnvStore.instance;
  }

  /**
   * Async startup hook to load environment variables.
   * Priority: process.env > Internal Store
   * (Standard Node.js behavior: existing env vars are not overwritten by .env)
   */
  public static async onStartup(envFile: string = '.env', logger?: IVaultFileLogger): Promise<LoadResult> {
    const instance = EnvStore.getInstance();
    if (logger) {
      instance.logger = logger;
    } else if (!instance.logger || instance.logger === getLogger()) {
      // Create default logger if none provided and still using global default
      instance.logger = Logger.create('vault-file', 'env-store');
    }

    instance.logger.info(`Starting EnvStore initialization from ${envFile}...`);
    instance._initialized = true;

    // Load from .env file
    if (fs.existsSync(envFile)) {
      instance.logger.debug(`Found env file at ${envFile}, parsing...`);
      const fileVars = parseEnvFile(envFile);
      const count = Object.keys(fileVars).length;
      instance.logger.debug(`Parsed ${count} variables from file.`);

      for (const [key, value] of Object.entries(fileVars)) {
        // Only set if not already in store (which is empty at start)
        instance.store[key] = value;
      }
    } else {
      instance.logger.warn(`Env file not found at ${envFile}`);
    }

    const processEnvCount = Object.keys(process.env).length;
    const storeCount = Object.keys(instance.store).length;
    instance._totalVarsLoaded = processEnvCount + storeCount; // Rough count

    instance.logger.info(`EnvStore initialized. Total accessible vars (approx): ${instance._totalVarsLoaded}`);

    return {
      totalVarsLoaded: instance._totalVarsLoaded
    };
  }

  public static get(key: string, defaultValue?: string): string | undefined {
    const instance = EnvStore.getInstance();
    // process.env takes precedence
    if (process.env[key] !== undefined) {
      return process.env[key];
    }
    if (instance.store[key] !== undefined) {
      return instance.store[key];
    }
    instance.logger.debug(`Env var '${key}' not found, using default: ${defaultValue}`);
    return defaultValue;
  }

  public static getOrThrow(key: string): string {
    const val = EnvStore.get(key);
    if (val === undefined) {
      const instance = EnvStore.getInstance();
      instance.logger.error(`Required env var '${key}' missing.`);
      throw new EnvKeyNotFoundError(key);
    }
    return val;
  }

  public static isInitialized(): boolean {
    return EnvStore.getInstance()._initialized;
  }
}

