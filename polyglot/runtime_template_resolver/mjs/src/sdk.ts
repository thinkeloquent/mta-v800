import { TemplateResolver } from './resolver.js';
import { IResolverOptions, ITemplateResolver } from './interfaces.js';
import { validatePlaceholder } from './validator.js';
import { extractPlaceholders } from './extractor.js';
import { compile as compileTemplate } from './compiler.js';

const defaultResolver = new TemplateResolver();

export const SDK = {
    resolve(template: string, context: Record<string, unknown>, options?: IResolverOptions): string {
        return defaultResolver.resolve(template, context, options);
    },
    resolveMany(templates: string[], context: Record<string, unknown>, options?: IResolverOptions): string[] {
        return templates.map(t => defaultResolver.resolve(t, context, options));
    },
    resolveObject(obj: unknown, context: Record<string, unknown>, options?: IResolverOptions): unknown {
        return defaultResolver.resolveObject(obj, context, options);
    },
    validate(template: string): void {
        const placeholders = extractPlaceholders(template);
        // split pipe for default values: key | "default"
        placeholders.forEach(p => {
            // Basic extraction of key part
            let key = p;
            if (p.includes('|')) {
                key = p.split('|')[0];
            }
            validatePlaceholder(key.trim());
        });
    },
    extract(template: string): string[] {
        return extractPlaceholders(template);
    },
    compile(template: string) {
        return compileTemplate(template);
    }
};
