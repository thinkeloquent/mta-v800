/**
 * Create a logger spy for testing log output.
 */
export declare function createLoggerSpy(): {
    logs: {
        debug: Array<{
            msg: string;
            data?: any;
        }>;
        info: Array<{
            msg: string;
            data?: any;
        }>;
        warn: Array<{
            msg: string;
            data?: any;
        }>;
        error: Array<{
            msg: string;
            data?: any;
            err?: any;
        }>;
    };
    mockLogger: {
        debug: (msg: string, data?: any) => number;
        info: (msg: string, data?: any) => number;
        warn: (msg: string, data?: any) => number;
        error: (msg: string, data?: any, err?: any) => number;
        trace: (msg: string, data?: any) => number;
    };
};
/**
 * Assert that logs contain expected text at specified level.
 */
export declare function expectLogContains(logs: ReturnType<typeof createLoggerSpy>['logs'], level: 'debug' | 'info' | 'warn' | 'error', text: string): void;
/**
 * Create a temporary .env file with given content.
 * Returns the file path. Caller is responsible for cleanup.
 */
export declare function createTempEnvFile(content: string): string;
/**
 * Clean up a temporary file.
 */
export declare function cleanupTempFile(filePath: string): void;
/**
 * Sample .env content for testing.
 */
export declare const sampleEnvContent = "# Sample environment file\nDATABASE_URL=postgres://localhost:5432/db\nAPI_KEY=\"secret-key-123\"\nDEBUG=true\nEMPTY_VALUE=\nQUOTED_VALUE='single quoted'\n";
/**
 * Sample VaultFile JSON for testing.
 */
export declare const sampleVaultFileJson: string;
//# sourceMappingURL=test-utils.d.ts.map