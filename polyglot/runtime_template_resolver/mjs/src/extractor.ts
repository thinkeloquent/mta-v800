import { logger } from './logger.js';

const log = logger.create('runtime-template-resolver', 'extractor.ts');

export function extractPlaceholders(template: string): string[] {
    log.debug('extractPlaceholders() called', { template });

    const matches = template.match(/{{([^}]+)}}/g);
    if (!matches) {
        log.debug('No placeholders found');
        return [];
    }

    const placeholders = matches.map(match => match.slice(2, -2).trim());
    log.debug('Placeholders extracted', { count: placeholders.length, placeholders });
    return placeholders;
}
