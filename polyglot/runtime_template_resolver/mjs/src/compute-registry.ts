/**
 * Compute function registry for runtime template resolution.
 *
 * Provides registration and execution of compute functions
 * used with the {{fn:function_name}} pattern.
 */

export enum ComputeScope {
  /** Resolved once at application startup */
  STARTUP = 'startup',
  /** Resolved per request */
  REQUEST = 'request'
}

export type ComputeFunction = (context?: Record<string, unknown>) => unknown;

export class ComputeFunctionError extends Error {
  name = 'ComputeFunctionError';

  constructor(message: string) {
    super(message);
  }
}

interface RegisteredFunction {
  fn: ComputeFunction;
  scope: ComputeScope;
}

/**
 * Registry for compute functions.
 *
 * @example
 * const registry = new ComputeRegistry();
 * registry.register('get_timestamp', () => new Date().toISOString());
 * registry.register('get_port', (ctx) => ctx?.PORT ?? 3000);
 *
 * const value = registry.resolve('get_timestamp'); // "2024-01-01T00:00:00.000Z"
 */
export class ComputeRegistry {
  /** Valid function name pattern: starts with letter or underscore, followed by alphanumerics/underscores */
  private static readonly NAME_PATTERN = /^[a-zA-Z_][a-zA-Z0-9_]*$/;

  private functions = new Map<string, RegisteredFunction>();

  /**
   * Register a compute function.
   *
   * @param name - Function name (used in {{fn:name}} pattern)
   * @param fn - Callable that takes optional context and returns a value
   * @param scope - When the function should be evaluated
   * @throws Error if name is invalid or already registered
   */
  register(
    name: string,
    fn: ComputeFunction,
    scope: ComputeScope = ComputeScope.STARTUP
  ): void {
    if (!name || !ComputeRegistry.NAME_PATTERN.test(name)) {
      throw new Error(`Invalid function name: ${name}`);
    }

    if (this.functions.has(name)) {
      throw new Error(`Function already registered: ${name}`);
    }

    this.functions.set(name, { fn, scope });
  }

  /**
   * Execute a registered compute function.
   *
   * @param name - Function name to execute
   * @param context - Optional context passed to the function
   * @returns Result of function execution
   * @throws ComputeFunctionError if function not found or execution fails
   */
  resolve(name: string, context?: Record<string, unknown>): unknown {
    const entry = this.functions.get(name);

    if (!entry) {
      throw new ComputeFunctionError(`Unknown compute function: ${name}`);
    }

    try {
      return entry.fn(context);
    } catch (e) {
      throw new ComputeFunctionError(
        `Error executing compute function '${name}': ${e instanceof Error ? e.message : e}`
      );
    }
  }

  /** Check if a function is registered. */
  has(name: string): boolean {
    return this.functions.has(name);
  }

  /** List all registered function names. */
  list(): string[] {
    return Array.from(this.functions.keys());
  }

  /** Get the scope of a registered function. */
  getScope(name: string): ComputeScope | undefined {
    return this.functions.get(name)?.scope;
  }

  /**
   * Unregister a compute function.
   *
   * @param name - Function name to unregister
   * @returns True if function was unregistered, false if not found
   */
  unregister(name: string): boolean {
    return this.functions.delete(name);
  }

  /** Remove all registered functions. */
  clear(): void {
    this.functions.clear();
  }
}
