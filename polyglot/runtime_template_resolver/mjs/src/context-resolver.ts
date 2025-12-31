/**
 * Context resolver bridging template and compute function resolution.
 *
 * Provides a unified API for resolving both {{variable.path}} templates
 * and {{fn:function_name}} compute functions.
 */

import { TemplateResolver } from './resolver.js';
import { ComputeRegistry } from './compute-registry.js';
import type { IResolverOptions } from './interfaces.js';

/**
 * Unified resolver for templates and compute functions.
 *
 * @example
 * const registry = new ComputeRegistry();
 * registry.register('get_port', () => 5432);
 *
 * const resolver = new ContextResolver(registry);
 *
 * // Template resolution
 * const result = resolver.resolve('{{host}}', { host: 'localhost' });
 *
 * // Compute function resolution
 * const port = resolver.resolve('{{fn:get_port}}', {});
 *
 * // Mixed object resolution
 * const config = resolver.resolveObject({
 *   host: '{{env.HOST}}',
 *   port: '{{fn:get_port}}'
 * }, { env: { HOST: 'localhost' } });
 */
export class ContextResolver {
  /** Pattern for compute functions: {{fn:function_name}} */
  private static readonly COMPUTE_PATTERN = /^\s*\{\{fn:(\w+)\}\}\s*$/;

  private templateResolver: TemplateResolver;
  private computeRegistry: ComputeRegistry;
  private defaultOptions?: IResolverOptions;

  /**
   * Initialize the context resolver.
   *
   * @param computeRegistry - Registry of compute functions (optional)
   * @param options - Default resolver options
   */
  constructor(
    computeRegistry?: ComputeRegistry,
    options?: IResolverOptions
  ) {
    this.templateResolver = new TemplateResolver();
    this.computeRegistry = computeRegistry ?? new ComputeRegistry();
    this.defaultOptions = options;
  }

  /** Check if expression is a compute function pattern. */
  isComputePattern(expression: string): boolean {
    return ContextResolver.COMPUTE_PATTERN.test(expression);
  }

  /**
   * Resolve a template or compute expression.
   *
   * @param expression - Template string or compute pattern
   * @param context - Context for template resolution
   * @param options - Override default resolver options
   * @returns Resolved value (string for templates, any for compute)
   */
  resolve(
    expression: string,
    context: Record<string, unknown>,
    options?: IResolverOptions
  ): unknown {
    const opts = options ?? this.defaultOptions;

    // Check for compute function pattern
    const match = expression.match(ContextResolver.COMPUTE_PATTERN);
    if (match) {
      const fnName = match[1];
      return this.computeRegistry.resolve(fnName, context);
    }

    // Fall back to template resolution
    return this.templateResolver.resolve(expression, context, opts);
  }

  /**
   * Recursively resolve templates and compute functions in an object.
   *
   * @param obj - Object containing template/compute expressions
   * @param context - Context for template resolution
   * @param options - Override default resolver options
   * @returns Object with all expressions resolved
   */
  resolveObject(
    obj: unknown,
    context: Record<string, unknown>,
    options?: IResolverOptions
  ): unknown {
    if (typeof obj === 'string') {
      return this.resolve(obj, context, options);
    }

    if (Array.isArray(obj)) {
      return obj.map(item => this.resolveObject(item, context, options));
    }

    if (obj !== null && typeof obj === 'object') {
      const result: Record<string, unknown> = {};
      for (const [key, value] of Object.entries(obj)) {
        result[key] = this.resolveObject(value, context, options);
      }
      return result;
    }

    return obj;
  }

  /**
   * Resolve multiple expressions with the same context.
   *
   * @param expressions - List of template/compute expressions
   * @param context - Shared context for resolution
   * @param options - Override default resolver options
   * @returns Array of resolved values
   */
  resolveMany(
    expressions: string[],
    context: Record<string, unknown>,
    options?: IResolverOptions
  ): unknown[] {
    return expressions.map(expr => this.resolve(expr, context, options));
  }
}
