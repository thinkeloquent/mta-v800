import { describe, it, expect, beforeEach } from '@jest/globals';
import { ContextResolver } from '../src/context-resolver.js';
import { ComputeRegistry, ComputeFunctionError } from '../src/compute-registry.js';
import { MissingStrategy } from '../src/interfaces.js';

describe('ContextResolver', () => {
  describe('template resolution', () => {
    let resolver: ContextResolver;

    beforeEach(() => {
      resolver = new ContextResolver();
    });

    it('resolves simple template', () => {
      const result = resolver.resolve('Hello {{name}}!', { name: 'World' });
      expect(result).toBe('Hello World!');
    });

    it('resolves nested template', () => {
      const result = resolver.resolve(
        'Welcome {{user.name}}!',
        { user: { name: 'Alice' } }
      );
      expect(result).toBe('Welcome Alice!');
    });

    it('resolves template with default value', () => {
      const result = resolver.resolve(
        "Host: {{host | 'localhost'}}",
        {}
      );
      expect(result).toBe('Host: localhost');
    });

    it('resolves multiple placeholders', () => {
      const result = resolver.resolve(
        '{{greeting}}, {{name}}!',
        { greeting: 'Hello', name: 'World' }
      );
      expect(result).toBe('Hello, World!');
    });
  });

  describe('compute function resolution', () => {
    let registry: ComputeRegistry;
    let resolver: ContextResolver;

    beforeEach(() => {
      registry = new ComputeRegistry();
      resolver = new ContextResolver(registry);
    });

    it('resolves compute function', () => {
      registry.register('get_port', () => 5432);
      const result = resolver.resolve('{{fn:get_port}}', {});
      expect(result).toBe(5432);
    });

    it('resolves compute function with context', () => {
      registry.register('get_env_port', (ctx) => ctx?.PORT ?? 3000);
      const result = resolver.resolve('{{fn:get_env_port}}', { PORT: 8080 });
      expect(result).toBe(8080);
    });

    it('resolves compute function with whitespace', () => {
      registry.register('get_value', () => 42);
      const result = resolver.resolve('  {{fn:get_value}}  ', {});
      expect(result).toBe(42);
    });

    it('throws on unknown compute function', () => {
      expect(() => resolver.resolve('{{fn:unknown}}', {}))
        .toThrow(ComputeFunctionError);
    });
  });

  describe('pattern detection', () => {
    let resolver: ContextResolver;

    beforeEach(() => {
      resolver = new ContextResolver();
    });

    it('isComputePattern returns true for compute patterns', () => {
      expect(resolver.isComputePattern('{{fn:test}}')).toBe(true);
      expect(resolver.isComputePattern('  {{fn:test}}  ')).toBe(true);
      expect(resolver.isComputePattern('{{fn:get_value}}')).toBe(true);
    });

    it('isComputePattern returns false for non-compute patterns', () => {
      expect(resolver.isComputePattern('{{name}}')).toBe(false);
      expect(resolver.isComputePattern('{{fn:test}} extra')).toBe(false);
      expect(resolver.isComputePattern('prefix {{fn:test}}')).toBe(false);
      expect(resolver.isComputePattern('{{user.name}}')).toBe(false);
      expect(resolver.isComputePattern('no placeholders')).toBe(false);
    });
  });

  describe('object resolution', () => {
    it('resolves object with templates', () => {
      const resolver = new ContextResolver();
      const obj = {
        host: '{{env.HOST}}',
        name: '{{app.name}}'
      };
      const context = {
        env: { HOST: 'localhost' },
        app: { name: 'myapp' }
      };
      const result = resolver.resolveObject(obj, context);
      expect(result).toEqual({ host: 'localhost', name: 'myapp' });
    });

    it('resolves object with compute functions', () => {
      const registry = new ComputeRegistry();
      registry.register('get_port', () => 5432);
      const resolver = new ContextResolver(registry);
      const obj = { port: '{{fn:get_port}}' };
      const result = resolver.resolveObject(obj, {});
      expect(result).toEqual({ port: 5432 });
    });

    it('resolves mixed object', () => {
      const registry = new ComputeRegistry();
      registry.register('get_port', () => 5432);
      const resolver = new ContextResolver(registry);

      const obj = {
        host: '{{env.HOST}}',
        port: '{{fn:get_port}}',
        name: 'static'
      };
      const context = { env: { HOST: 'localhost' } };

      const result = resolver.resolveObject(obj, context);
      expect(result).toEqual({
        host: 'localhost',
        port: 5432,
        name: 'static'
      });
    });

    it('resolves nested object', () => {
      const registry = new ComputeRegistry();
      registry.register('get_port', () => 5432);
      const resolver = new ContextResolver(registry);

      const obj = {
        database: {
          host: '{{db.host}}',
          port: '{{fn:get_port}}'
        },
        api: {
          url: '{{api.url}}'
        }
      };
      const context = {
        db: { host: 'db.example.com' },
        api: { url: 'https://api.example.com' }
      };

      const result = resolver.resolveObject(obj, context);
      expect(result).toEqual({
        database: {
          host: 'db.example.com',
          port: 5432
        },
        api: {
          url: 'https://api.example.com'
        }
      });
    });

    it('resolves object with arrays', () => {
      const resolver = new ContextResolver();
      const obj = {
        items: ['{{items[0]}}', '{{items[1]}}']
      };
      const context = { items: ['first', 'second'] };
      const result = resolver.resolveObject(obj, context);
      expect(result).toEqual({ items: ['first', 'second'] });
    });

    it('preserves non-string values', () => {
      const resolver = new ContextResolver();
      const obj = {
        name: '{{name}}',
        count: 42,
        enabled: true,
        data: null
      };
      const result = resolver.resolveObject(obj, { name: 'test' });
      expect(result).toEqual({
        name: 'test',
        count: 42,
        enabled: true,
        data: null
      });
    });
  });

  describe('resolve many', () => {
    it('resolves multiple templates', () => {
      const resolver = new ContextResolver();
      const expressions = ['{{name}}', '{{greeting}}'];
      const results = resolver.resolveMany(
        expressions,
        { name: 'World', greeting: 'Hello' }
      );
      expect(results).toEqual(['World', 'Hello']);
    });

    it('resolves multiple mixed expressions', () => {
      const registry = new ComputeRegistry();
      registry.register('get_port', () => 5432);
      const resolver = new ContextResolver(registry);

      const expressions = ['{{name}}', '{{fn:get_port}}'];
      const results = resolver.resolveMany(expressions, { name: 'test' });
      expect(results).toEqual(['test', 5432]);
    });

    it('resolves empty list', () => {
      const resolver = new ContextResolver();
      const results = resolver.resolveMany([], {});
      expect(results).toEqual([]);
    });
  });

  describe('with options', () => {
    it('uses default options', () => {
      const options = { missingStrategy: MissingStrategy.KEEP };
      const resolver = new ContextResolver(undefined, options);

      const result = resolver.resolve('{{missing}}', {});
      expect(result).toBe('{{missing}}');
    });

    it('overrides options per call', () => {
      const defaultOptions = { missingStrategy: MissingStrategy.KEEP };
      const resolver = new ContextResolver(undefined, defaultOptions);

      const overrideOptions = { missingStrategy: MissingStrategy.EMPTY };
      const result = resolver.resolve('{{missing}}', {}, overrideOptions);
      expect(result).toBe('');
    });
  });
});
