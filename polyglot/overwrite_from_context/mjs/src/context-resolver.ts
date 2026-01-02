
import _ from 'lodash';
const { get } = _;
import { Logger } from './logger.js';
import { ComputeScope, MissingStrategy, ResolverOptions } from './options.js';
import {
    ComputeFunctionError,
    RecursionLimitError,
    ScopeViolationError,
    ErrorCode,
    SecurityError
} from './errors.js';
import { ComputeRegistry } from './compute-registry.js';
import { Security } from './security.js';

export class ContextResolver {
    // {{fn:name | "default"}}
    private static COMPUTE_PATTERN = /^\{\{fn:([a-zA-Z_][a-zA-Z0-9_]*)(\s*\|\s*['"](.*)['"])?\}\}$/;

    // {{variable.path | "default"}}
    private static TEMPLATE_PATTERN = /^\{\{([a-zA-Z0-9_.]*)(\s*\|\s*['"](.*)['"])?\}\}$/;

    private logger: Logger;
    private registry: ComputeRegistry;
    private maxDepth: number;
    private missingStrategy: MissingStrategy;

    constructor(registry: ComputeRegistry, options?: ResolverOptions) {
        this.logger = options?.logger || Logger.create('runtime-template-resolver', 'context-resolver.ts');
        this.registry = registry;
        this.maxDepth = options?.maxDepth ?? 10;
        this.missingStrategy = options?.missingStrategy ?? MissingStrategy.ERROR;
        this.logger.debug('ContextResolver initialized');
    }

    public isComputePattern(expression: string): boolean {
        return ContextResolver.COMPUTE_PATTERN.test(expression);
    }

    public async resolve(
        expression: any,
        context: Record<string, any>,
        scope: ComputeScope = ComputeScope.REQUEST,
        depth: number = 0
    ): Promise<any> {
        // Pass-through non-string values
        if (typeof expression !== 'string') {
            return expression;
        }

        // Recursion check
        if (depth > this.maxDepth) {
            throw new RecursionLimitError(
                `Recursion limit reached (${this.maxDepth})`,
                ErrorCode.RECURSION_LIMIT
            );
        }

        // Check compute pattern first
        const computeMatch = ContextResolver.COMPUTE_PATTERN.exec(expression);
        if (computeMatch) {
            return this.resolveCompute(computeMatch, context, scope);
        }

        // Check template pattern
        const templateMatch = ContextResolver.TEMPLATE_PATTERN.exec(expression);
        if (templateMatch) {
            return this.resolveTemplate(templateMatch, context);
        }

        // Otherwise return literal string
        return expression;
    }

    public async resolveObject(
        obj: any,
        context: Record<string, any>,
        scope: ComputeScope = ComputeScope.REQUEST,
        depth: number = 0
    ): Promise<any> {
        if (depth > this.maxDepth) {
            throw new RecursionLimitError(
                `Recursion limit reached (${this.maxDepth})`,
                ErrorCode.RECURSION_LIMIT
            );
        }

        if (Array.isArray(obj)) {
            return Promise.all(obj.map(item => this.resolveObject(item, context, scope, depth + 1)));
        }

        if (obj !== null && typeof obj === 'object') {
            const newObj: Record<string, any> = {};
            for (const key of Object.keys(obj)) {
                newObj[key] = await this.resolveObject(obj[key], context, scope, depth + 1);
            }
            return newObj;
        }

        if (typeof obj === 'string') {
            return this.resolve(obj, context, scope, depth);
        }

        return obj;
    }

    public async resolveMany(
        expressions: any[],
        context: Record<string, any>,
        scope: ComputeScope = ComputeScope.REQUEST
    ): Promise<any[]> {
        return Promise.all(expressions.map(expr => this.resolve(expr, context, scope)));
    }

    private async resolveCompute(match: RegExpExecArray, context: Record<string, any>, scope: ComputeScope): Promise<any> {
        const fnName = match[1];
        const defaultVal = match[3];

        this.logger.debug(`Resolving compute: ${fnName}, default: ${defaultVal}`);

        if (!this.registry.has(fnName)) {
            if (defaultVal !== undefined) {
                return this.parseDefault(defaultVal);
            }
            if (this.missingStrategy === MissingStrategy.DEFAULT) return undefined;
            if (this.missingStrategy === MissingStrategy.IGNORE) return match[0];

            throw new ComputeFunctionError(
                `Compute function not found: ${fnName}`,
                ErrorCode.COMPUTE_FUNCTION_NOT_FOUND,
                { name: fnName }
            );
        }

        // Skip REQUEST-scoped functions during STARTUP (leave for request-time resolution)
        const fnScope = this.registry.getScope(fnName);
        if (fnScope === ComputeScope.REQUEST && scope === ComputeScope.STARTUP) {
            this.logger.debug(`Skipping REQUEST scope function '${fnName}' during STARTUP (will resolve at request time)`);
            return match[0];  // Return original template string
        }

        try {
            return await this.registry.resolve(fnName, context);
        } catch (e: any) {
            if (defaultVal !== undefined) {
                this.logger.warn(`Function ${fnName} failed, using default: ${e.message}`);
                return this.parseDefault(defaultVal);
            }
            throw e;
        }
    }

    private resolveTemplate(match: RegExpExecArray, context: Record<string, any>): any {
        const path = match[1];
        const defaultVal = match[3];

        this.logger.debug(`Resolving template: ${path}, default: ${defaultVal}`);

        Security.validatePath(path);

        const val = get(context, path);

        if (val === undefined) {
            if (defaultVal !== undefined) {
                return this.parseDefault(defaultVal);
            }
            if (this.missingStrategy === MissingStrategy.IGNORE) return match[0];
            // Return undefined if missing (caller handles?) or if explicit strategy
        }

        return val !== undefined ? val : (defaultVal !== undefined ? this.parseDefault(defaultVal) : match[0]); // Fallback logic slightly different?
    }

    private parseDefault(val: string): any {
        if (val === 'true') return true;
        if (val === 'false') return false;
        if (!isNaN(Number(val))) return Number(val);
        return val;
    }
}
