import { program } from 'commander';
import { ConfigSDK, ComputeScope } from './sdk.js';

program
    .name('config-sdk')
    .description('Polyglot Config SDK CLI')
    .version('1.0.0');

program
    .command('show')
    .description('Show resolved configuration')
    .action(async () => {
        try {
            const sdk = await ConfigSDK.initialize();
            const resolved = await sdk.getResolved(ComputeScope.STARTUP);
            console.log(JSON.stringify(resolved, null, 2));
        } catch (e: any) {
            console.error("Error:", e.message);
            process.exit(1);
        }
    });

program
    .command('resolve <template>')
    .option('--allow-errors', 'Return original string on resolution failure') // Recommendation 3
    .description('Resolve a specific template string')
    .action(async (template, options) => {
        try {
            const sdk = await ConfigSDK.initialize();
            // Mock simple resolve - real impl would use resolver.resovleString
            console.log(`Resolving ${template}... (Mock)`);
        } catch (e: any) {
            if (options.allowErrors) {
                console.log(template);
            } else {
                console.error("Error:", e.message);
                process.exit(1);
            }
        }
    });

program.parse();
