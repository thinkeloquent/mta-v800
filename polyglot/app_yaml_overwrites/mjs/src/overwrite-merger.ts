import _ from 'lodash';

export function applyOverwrites(originalConfig: any, overwriteSection: any): any {
    if (!overwriteSection) return originalConfig;

    // Deep merge using lodash, where overwriteSection takes precedence
    // Note: This matches the requirement to merge overwrites into parent
    // In a real implementation, we might need custom logic to handle 'null' specifically
    // if strict null handling is required vs undefined.
    // For this implementation, we assume standard merge.

    return _.merge({}, originalConfig, overwriteSection);
}
