import { describe, it, expect, beforeEach } from '@jest/globals';
import {
  ComputeRegistry,
  ComputeScope,
  ComputeFunctionError
} from '../src/compute-registry.js';

describe('ComputeRegistry', () => {
  let registry: ComputeRegistry;

  beforeEach(() => {
    registry = new ComputeRegistry();
  });

  describe('basic registration and resolution', () => {
    it('registers and resolves simple function', () => {
      registry.register('get_value', () => 42);
      expect(registry.resolve('get_value')).toBe(42);
    });

    it('resolves with context', () => {
      registry.register('get_host', (ctx) => ctx?.HOST ?? 'localhost');
      expect(registry.resolve('get_host', { HOST: 'prod.example.com' }))
        .toBe('prod.example.com');
    });

    it('resolves with context using default value', () => {
      registry.register('get_host', (ctx) => ctx?.HOST ?? 'localhost');
      expect(registry.resolve('get_host', {})).toBe('localhost');
    });

    it('resolves function without context when context is passed', () => {
      registry.register('get_constant', () => 'constant_value');
      expect(registry.resolve('get_constant', { unused: 'data' })).toBe('constant_value');
    });

    it('returns various types', () => {
      registry.register('get_int', () => 42);
      registry.register('get_float', () => 3.14);
      registry.register('get_dict', () => ({ key: 'value' }));
      registry.register('get_list', () => [1, 2, 3]);
      registry.register('get_bool', () => true);
      registry.register('get_null', () => null);

      expect(registry.resolve('get_int')).toBe(42);
      expect(registry.resolve('get_float')).toBe(3.14);
      expect(registry.resolve('get_dict')).toEqual({ key: 'value' });
      expect(registry.resolve('get_list')).toEqual([1, 2, 3]);
      expect(registry.resolve('get_bool')).toBe(true);
      expect(registry.resolve('get_null')).toBe(null);
    });
  });

  describe('error handling', () => {
    it('throws on unknown function', () => {
      expect(() => registry.resolve('unknown'))
        .toThrow(ComputeFunctionError);
      expect(() => registry.resolve('unknown'))
        .toThrow('Unknown compute function');
    });

    it('throws on duplicate registration', () => {
      registry.register('fn', () => 1);
      expect(() => registry.register('fn', () => 2))
        .toThrow('already registered');
    });

    it('throws on empty function name', () => {
      expect(() => registry.register('', () => 1))
        .toThrow('Invalid function name');
    });

    it('throws on function name with hyphen', () => {
      expect(() => registry.register('invalid-name', () => 1))
        .toThrow('Invalid function name');
    });

    it('throws on function name starting with number', () => {
      expect(() => registry.register('1invalid', () => 1))
        .toThrow('Invalid function name');
    });

    it('wraps function execution errors', () => {
      registry.register('failing_fn', () => { throw new Error('fail'); });
      expect(() => registry.resolve('failing_fn'))
        .toThrow(ComputeFunctionError);
      expect(() => registry.resolve('failing_fn'))
        .toThrow('Error executing');
    });
  });

  describe('valid function names', () => {
    it('accepts underscore in function name', () => {
      registry.register('get_value', () => 1);
      expect(registry.has('get_value')).toBe(true);
    });

    it('accepts function name starting with underscore', () => {
      registry.register('_private_fn', () => 1);
      expect(registry.has('_private_fn')).toBe(true);
    });

    it('accepts function name with numbers', () => {
      registry.register('get_v2', () => 2);
      expect(registry.has('get_v2')).toBe(true);
    });
  });

  describe('utility methods', () => {
    it('has() returns true for registered', () => {
      registry.register('exists', () => 1);
      expect(registry.has('exists')).toBe(true);
    });

    it('has() returns false for missing', () => {
      expect(registry.has('missing')).toBe(false);
    });

    it('list() returns all function names', () => {
      registry.register('fn1', () => 1);
      registry.register('fn2', () => 2);
      registry.register('fn3', () => 3);
      expect(registry.list().sort()).toEqual(['fn1', 'fn2', 'fn3']);
    });

    it('list() returns empty array when empty', () => {
      expect(registry.list()).toEqual([]);
    });

    it('getScope() returns correct scope', () => {
      registry.register('startup_fn', () => 1, ComputeScope.STARTUP);
      registry.register('request_fn', () => 2, ComputeScope.REQUEST);
      expect(registry.getScope('startup_fn')).toBe(ComputeScope.STARTUP);
      expect(registry.getScope('request_fn')).toBe(ComputeScope.REQUEST);
    });

    it('getScope() returns undefined for missing', () => {
      expect(registry.getScope('missing')).toBeUndefined();
    });

    it('default scope is STARTUP', () => {
      registry.register('fn', () => 1);
      expect(registry.getScope('fn')).toBe(ComputeScope.STARTUP);
    });

    it('unregister() removes function', () => {
      registry.register('fn', () => 1);
      expect(registry.unregister('fn')).toBe(true);
      expect(registry.has('fn')).toBe(false);
    });

    it('unregister() returns false for missing', () => {
      expect(registry.unregister('missing')).toBe(false);
    });

    it('clear() removes all functions', () => {
      registry.register('fn1', () => 1);
      registry.register('fn2', () => 2);
      registry.clear();
      expect(registry.has('fn1')).toBe(false);
      expect(registry.has('fn2')).toBe(false);
      expect(registry.list()).toEqual([]);
    });
  });
});
