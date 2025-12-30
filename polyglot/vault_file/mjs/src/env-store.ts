import fs from 'fs';
import path from 'path';
import { LoadResult } from './domain.js';
import { parseEnvFile } from './core.js';
import { EnvKeyNotFoundError } from './validators.js';

export class EnvStore {
  private static instance: EnvStore;
  private store: Record<string, string> = {};
  private _initialized = false;
  private _totalVarsLoaded = 0;

  private constructor() {}

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
  public static async onStartup(envFile: string = '.env'): Promise<LoadResult> {
    const instance = EnvStore.getInstance();
    instance._initialized = true;

    // Load from .env file
    if (fs.existsSync(envFile)) {
        const fileVars = parseEnvFile(envFile);
        for (const [key, value] of Object.entries(fileVars)) {
            // Only set if not already in store (which is empty at start)
            // But what about process.env?
            // "Node.js: process.env > Store"
            // So we store it in our internal store?
            // Or we check process.env in get()?
            
            // Let's populate store with file vars.
            // But if process.env has it, that takes precedence?
            instance.store[key] = value;
        }
    }
    
    // In strict Node logic "process.env > .env", usually .env libraries don't overwrite process.env.
    // So if I have:
    // process.env.FOO = 'sys'
    // .env has FOO=file
    // get('FOO') should return 'sys'.
    
    // Implementation of get():
    // return process.env[key] || this.store[key]
    
    instance._totalVarsLoaded = Object.keys(process.env).length + Object.keys(instance.store).length; // Rough count
    
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
    return defaultValue;
  }

  public static getOrThrow(key: string): string {
    const val = EnvStore.get(key);
    if (val === undefined) {
        throw new EnvKeyNotFoundError(key);
    }
    return val;
  }

  public static isInitialized(): boolean {
      return EnvStore.getInstance()._initialized;
  }
}
