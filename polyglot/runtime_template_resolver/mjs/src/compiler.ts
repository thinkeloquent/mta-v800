import { logger } from './logger.js';
import { TemplateResolver } from './resolver.js';
import { ITemplateResolver } from './interfaces.js';

const log = logger.create('runtime-template-resolver', 'compiler.ts');
const textResolver: ITemplateResolver = new TemplateResolver();

export function compile(template: string): (context: Record<string, unknown>) => string {
    log.debug('Compiling template', { template });
    return (context: Record<string, unknown>) => {
        return textResolver.resolve(template, context);
    };
}
