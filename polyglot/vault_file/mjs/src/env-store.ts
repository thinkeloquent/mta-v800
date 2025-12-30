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
    this.logger = Logger.create('vault-file', 'env-store.ts');
    this.logger.debug('EnvStore instance created');
  }

  public static getInstance(): EnvStore {
    if (!EnvStore.instance) {
      EnvStore.instance = new EnvStore();
      EnvStore.instance.logger.debug('EnvStore singleton initialized');
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
      instance.logger.debug('Custom logger injected into EnvStore');
    }

    instance.logger.info('=== EnvStore Startup Begin ===');
    instance.logger.info('onStartup() called', { envFile });

    if (!envFile) {
      instance.logger.error('onStartup() called with empty envFile path');
      throw new Error('Environment file path is required');
    }

    instance._initialized = true;
    instance.logger.debug('EnvStore marked as initialized');

    // Load from .env file
    if (fs.existsSync(envFile)) {
      instance.logger.info('Env file found', { envFile });

      try {
        const fileVars = parseEnvFile(envFile);
        const count = Object.keys(fileVars).length;

        if (count === 0) {
          instance.logger.warn('Env file exists but contains no variables', { envFile });
        } else {
          instance.logger.info('Successfully parsed env file', { envFile, variableCount: count });

          for (const [key, value] of Object.entries(fileVars)) {
            instance.store[key] = value;
            instance.logger.debug('Loaded env var into store', { key });
          }
        }
      } catch (err) {
        instance.logger.error('Failed to parse env file', { envFile }, err as Error);
        throw err;
      }
    } else {
      instance.logger.warn('Env file NOT FOUND - this may cause missing configuration', { envFile });
      instance.logger.warn('Expected file location:', { absolutePath: path.resolve(envFile) });
    }

    const processEnvCount = Object.keys(process.env).length;
    const storeCount = Object.keys(instance.store).length;
    instance._totalVarsLoaded = processEnvCount + storeCount;

    instance.logger.info('=== EnvStore Startup Complete ===', {
      processEnvVars: processEnvCount,
      fileVars: storeCount,
      totalAccessible: instance._totalVarsLoaded
    });

    return {
      totalVarsLoaded: instance._totalVarsLoaded
    };
  }

  public static get(key: string, defaultValue?: string): string | undefined {
    const instance = EnvStore.getInstance();

    if (!key) {
      instance.logger.warn('get() called with empty key');
      return defaultValue;
    }

    // process.env takes precedence
    if (process.env[key] !== undefined) {
      instance.logger.debug('Env var found in process.env', { key });
      return process.env[key];
    }

    if (instance.store[key] !== undefined) {
      instance.logger.debug('Env var found in internal store', { key });
      return instance.store[key];
    }

    if (defaultValue !== undefined) {
      instance.logger.debug('Env var not found, using default', { key, hasDefault: true });
    } else {
      instance.logger.debug('Env var not found, no default provided', { key });
    }

    return defaultValue;
  }

  public static getOrThrow(key: string): string {
    const instance = EnvStore.getInstance();

    if (!key) {
      instance.logger.error('getOrThrow() called with empty key');
      throw new Error('Key is required');
    }

    instance.logger.debug('getOrThrow() called', { key });

    const val = EnvStore.get(key);
    if (val === undefined) {
      instance.logger.error('REQUIRED ENV VAR MISSING', {
        key,
        hint: `Please ensure '${key}' is set in your .env file or environment`
      });
      throw new EnvKeyNotFoundError(key);
    }

    instance.logger.debug('getOrThrow() succeeded', { key });
    return val;
  }

  public static isInitialized(): boolean {
    const initialized = EnvStore.getInstance()._initialized;
    EnvStore.getInstance().logger.debug('isInitialized() called', { initialized });
    return initialized;
  }
}

