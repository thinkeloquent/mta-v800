import { toJSON, fromJSON } from '../src/core';
import { VaultFile } from '../src/domain';

describe('Vault File Parity', () => {
    it('should normalize version to 1.0.0 on load', () => {
        const json = '{"header": {"version": "1.0"}, "secrets": {}}';
        const loaded = fromJSON(json);
        expect(loaded.header.version).toBe("1.0.0");
    });

    it('should serialize keys to snake_case', () => {
        const file: VaultFile = {
            header: {
                version: "1.0.0",
                createdAt: "2023-01-01T00:00:00.000Z"
            },
            secrets: { "MY_SECRET": "value" }
        };
        const json = toJSON(file);
        const parsed = JSON.parse(json);
        expect(parsed.header.created_at).toBeDefined();
        expect(parsed.header.createdAt).toBeUndefined();
    });
});
