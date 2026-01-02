import { Logger } from './logger.js';
import { ComputeScope } from './options.js';
import { ComputeFunctionError, ErrorCode } from './errors.js';

type ComputeFunction = (context?: any) => any | Promise<any>;

interface RegisteredFunction {
    fn: ComputeFunction;
    scope: ComputeScope;
}

export class ComputeRegistry {
    private logger: Logger;
    private functions: Map<string, RegisteredFunction>;
    private cache: Map<string, any>;
    private static NAME_PATTERN = /^[a-zA-Z_][a-zA-Z0-9_]*$/;

    constructor(logger?: Logger) {
        this.logger = logger || Logger.create('runtime-template-resolver', 'compute-registry.ts'); // Using static filename as __filename is not available in ESM easily without helpers
        this.functions = new Map();
        this.cache = new Map();
        this.logger.debug('ComputeRegistry initialized');
    }

    public register(name: string, fn: ComputeFunction, scope: ComputeScope): void {
        this.validateName(name);
        this.logger.debug(`Registering function: ${name} with scope: ${scope}`);
        this.functions.set(name, { fn, scope });
        this.logger.info(`Function registered: ${name}`);
    }

    public unregister(name: string): void {
        if (this.functions.has(name)) {
            this.logger.debug(`Unregistering function: ${name}`);
            this.functions.delete(name);
            this.logger.info(`Function unregistered: ${name}`);
        }
    }

    public has(name: string): boolean {
        return this.functions.has(name);
    }

    public list(): string[] {
        return Array.from(this.functions.keys());
    }

    public getScope(name: string): ComputeScope | undefined {
        return this.functions.get(name)?.scope;
    }

    public clear(): void {
        this.logger.debug('Clearing registry');
        this.functions.clear();
        this.cache.clear();
    }

    public clearCache(): void {
        this.logger.debug('Clearing result cache');
        this.cache.clear();
    }

    public async resolve(name: string, context?: any): Promise<any> {
        this.logger.debug(`Resolving function: ${name}`);

        const regFn = this.functions.get(name);
        if (!regFn) {
            throw new ComputeFunctionError(
                `Compute function not found: ${name}`,
                ErrorCode.COMPUTE_FUNCTION_NOT_FOUND,
                { name }
            );
        }

        // Check cache for STARTUP functions
        if (regFn.scope === ComputeScope.STARTUP && this.cache.has(name)) {
            this.logger.debug(`Returning cached value for: ${name}`);
            return this.cache.get(name);
        }

        try {
            const result = await regFn.fn(context);

            // Cache result if STARTUP scope
            if (regFn.scope === ComputeScope.STARTUP) {
                this.cache.set(name, result);
            }

            return result;
        } catch (e: any) {
            this.logger.error(`Function execution failed: ${name}, error: ${e.message}`);
            throw new ComputeFunctionError(
                `Compute function failed: ${name}`,
                ErrorCode.COMPUTE_FUNCTION_FAILED,
                { name, originalError: e.message }
            );
        }
    }

    private validateName(name: string): void {
        if (!name) {
            throw new Error('Function name cannot be empty');
        }
        if (!ComputeRegistry.NAME_PATTERN.test(name)) {
            throw new Error(`Invalid function name: ${name}. Must match pattern: ^[a-zA-Z_][a-zA-Z0-9_]*$`);
        }
    }
}
