/**
 * Parses a path string into segments.
 * Supports dot notation and bracket notation.
 * e.g. "a.b[0]" -> ["a", "b", "0"]
 */
export function parsePath(path: string): string[] {
    const segments: string[] = [];
    let current = '';
    let inBracket = false;
    let inQuote: string | null = null;

    for (let i = 0; i < path.length; i++) {
        const char = path[i];

        if (inQuote) {
            if (char === inQuote) {
                inQuote = null;
            } else {
                current += char;
            }
            continue;
        }

        if (char === '"' || char === "'") {
            inQuote = char;
            continue;
        }

        if (char === '[') {
            if (current) {
                segments.push(current);
                current = '';
            }
            inBracket = true;
            continue;
        }

        if (char === ']') {
            if (current) {
                segments.push(current);
                current = '';
            }
            inBracket = false;
            continue;
        }

        if (char === '.' && !inBracket) {
            if (current) segments.push(current);
            current = '';
            continue;
        }

        current += char;
    }

    if (current) segments.push(current);
    return segments;
}
