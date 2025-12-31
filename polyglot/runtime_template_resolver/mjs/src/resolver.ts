import { logger } from './logger.js';
import { ITemplateResolver, IResolverOptions, MissingStrategy } from './interfaces.js';
import { SecurityError } from './errors.js';
import { parsePath } from './path-parser.js';
import { validatePlaceholder } from './validator.js';
import { toString } from './coercion.js';
import { handleMissing } from './missing-handler.js';
import { resolveObject } from './batch.js';

const log = logger.create('runtime-template-resolver', 'resolver.ts');

export class TemplateResolver implements ITemplateResolver {
    resolve(template: string, context: Record<string, unknown>, options?: IResolverOptions): string {
        log.debug('resolve() called', { templateLength: template.length });
        const effectiveLog = options?.logger || log;
        const missingStrategy = options?.missingStrategy || MissingStrategy.EMPTY;
        const throwOnError = options?.throwOnError || false;

        return template.replace(/{{([^}]+)}}/g, (match, inner) => {
            const rawInner = inner.trim();
            let key = rawInner;
            let defaultValue: string | undefined;

            if (key.includes('|')) {
                const parts = key.split('|');
                key = parts[0].trim();
                const defaultPart = parts.slice(1).join('|').trim();
                if ((defaultPart.startsWith('"') && defaultPart.endsWith('"')) ||
                    (defaultPart.startsWith("'") && defaultPart.endsWith("'"))) {
                    defaultValue = defaultPart.slice(1, -1);
                } else {
                    defaultValue = defaultPart;
                }
            }

            try {
                validatePlaceholder(key);
                const segments = parsePath(key);
                let current: any = context;

                for (const segment of segments) {
                    if (segment.startsWith('_')) {
                        const msg = `Access to private/unsafe attribute '${segment}' is denied`;
                        effectiveLog.warn(msg, { segment });
                        throw new SecurityError(msg);
                    }

                    if (current === undefined || current === null) {
                        current = undefined;
                        break;
                    }

                    if (typeof current === 'object') {
                        if (Array.isArray(current)) {
                            const idx = parseInt(segment, 10);
                            if (!isNaN(idx)) {
                                current = current[idx];
                            } else {
                                current = undefined;
                            }
                        } else {
                            current = (current as any)[segment];
                        }
                    } else {
                        current = undefined;
                        break;
                    }
                }

                if (current === undefined) {
                    if (defaultValue !== undefined) return defaultValue;
                    return handleMissing(key, missingStrategy, defaultValue);
                }

                return toString(current);

            } catch (err: any) {
                effectiveLog.error(err.message, { key: rawInner });
                if (throwOnError) throw err;
                return match;
            }
        });
    }

    resolveObject(obj: unknown, context: Record<string, unknown>, options?: IResolverOptions): unknown {
        return resolveObject(obj, context, this, options);
    }
}
