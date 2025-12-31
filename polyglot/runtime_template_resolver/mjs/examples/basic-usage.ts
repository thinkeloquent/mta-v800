#!/usr/bin/env npx tsx
/**
 * Runtime Template Resolver - Basic Usage Examples
 *
 * This script demonstrates core features of the runtime_template_resolver package:
 * - Simple placeholder resolution
 * - Nested path resolution
 * - Default values
 * - Missing value strategies
 * - Object/config resolution
 * - Template compilation
 * - Placeholder extraction and validation
 */

import {
    TemplateResolver,
    SDK,
    MissingStrategy,
    SecurityError,
    ValidationError,
    MissingValueError,
    validatePlaceholder,
    extractPlaceholders,
} from '../src/index.js';

// =============================================================================
// Example 1: Simple Placeholder Resolution
// =============================================================================
function example1_simpleResolution(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 1: Simple Placeholder Resolution');
    console.log('='.repeat(60));

    const resolver = new TemplateResolver();

    const template = 'Hello, {{name}}! Welcome to {{company}}.';
    const context = { name: 'Alice', company: 'ACME Corp' };

    const result = resolver.resolve(template, context);
    console.log(`Template: ${template}`);
    console.log(`Context:  ${JSON.stringify(context)}`);
    console.log(`Result:   ${result}`);
}

// =============================================================================
// Example 2: Nested Path Resolution
// =============================================================================
function example2_nestedPaths(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 2: Nested Path Resolution');
    console.log('='.repeat(60));

    const resolver = new TemplateResolver();

    const template = 'User {{user.profile.name}} ({{user.profile.email}}) has role: {{user.role}}';
    const context = {
        user: {
            profile: {
                name: 'Bob Smith',
                email: 'bob@example.com'
            },
            role: 'admin'
        }
    };

    const result = resolver.resolve(template, context);
    console.log(`Template: ${template}`);
    console.log(`Result:   ${result}`);
}

// =============================================================================
// Example 3: Array Access
// =============================================================================
function example3_arrayAccess(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 3: Array Access');
    console.log('='.repeat(60));

    const resolver = new TemplateResolver();

    const template = 'Top items: {{items[0]}}, {{items[1]}}, {{items[2]}}';
    const context = {
        items: ['Apple', 'Banana', 'Cherry', 'Date']
    };

    const result = resolver.resolve(template, context);
    console.log(`Template: ${template}`);
    console.log(`Result:   ${result}`);
}

// =============================================================================
// Example 4: Default Values
// =============================================================================
function example4_defaultValues(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 4: Default Values');
    console.log('='.repeat(60));

    const resolver = new TemplateResolver();

    const templates: Array<[string, Record<string, unknown>]> = [
        ['DB Host: {{db.host | "localhost"}}', {}],
        ["DB Port: {{db.port | '5432'}}", {}],
        ['Environment: {{env | production}}', {}],
        ['API Key: {{api_key | "not-set"}}', { api_key: 'secret-123' }],
    ];

    for (const [template, context] of templates) {
        const result = resolver.resolve(template, context);
        console.log(`Template: ${template}`);
        console.log(`Result:   ${result}`);
        console.log();
    }
}

// =============================================================================
// Example 5: Missing Value Strategies
// =============================================================================
function example5_missingStrategies(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 5: Missing Value Strategies');
    console.log('='.repeat(60));

    const resolver = new TemplateResolver();
    const template = 'Value: {{missing_key}}';
    const context = {};

    const strategies: Array<[MissingStrategy, string]> = [
        [MissingStrategy.EMPTY, 'Replace with empty string'],
        [MissingStrategy.KEEP, 'Keep original placeholder'],
        [MissingStrategy.DEFAULT, 'Use default value (empty if none)'],
    ];

    for (const [strategy, description] of strategies) {
        const result = resolver.resolve(template, context, { missingStrategy: strategy });
        console.log(`Strategy ${strategy}: ${description}`);
        console.log(`  Result: '${result}'`);
        console.log();
    }

    // ERROR strategy throws exception
    console.log('Strategy ERROR: Throws exception');
    try {
        resolver.resolve(template, context, {
            missingStrategy: MissingStrategy.ERROR,
            throwOnError: true
        });
    } catch (e) {
        if (e instanceof MissingValueError) {
            console.log(`  Caught: ${e.message}`);
        }
    }
}

// =============================================================================
// Example 6: Resolve Object (Config Templates)
// =============================================================================
function example6_resolveObject(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 6: Resolve Object (Config Templates)');
    console.log('='.repeat(60));

    const resolver = new TemplateResolver();

    const config = {
        database: {
            url: 'postgres://{{db.host}}:{{db.port}}/{{db.name}}',
            poolSize: 10
        },
        api: {
            baseUrl: 'https://{{api.domain}}/v{{api.version}}',
            endpoints: [
                '/users/{{user_id}}',
                '/orders/{{order_id}}'
            ]
        },
        messages: {
            welcome: 'Welcome {{user.name}} to {{app.name}}!'
        }
    };

    const context = {
        db: { host: 'localhost', port: '5432', name: 'myapp' },
        api: { domain: 'api.example.com', version: '2' },
        user_id: '123',
        order_id: '456',
        user: { name: 'Alice' },
        app: { name: 'MyApp' }
    };

    const resolved = resolver.resolveObject(config, context) as typeof config;

    console.log('Original config with templates:');
    console.log(`  database.url: ${config.database.url}`);
    console.log(`  api.baseUrl: ${config.api.baseUrl}`);
    console.log();
    console.log('Resolved config:');
    console.log(`  database.url: ${resolved.database.url}`);
    console.log(`  api.baseUrl: ${resolved.api.baseUrl}`);
    console.log(`  api.endpoints: ${JSON.stringify(resolved.api.endpoints)}`);
    console.log(`  messages.welcome: ${resolved.messages.welcome}`);
}

// =============================================================================
// Example 7: Template Compilation
// =============================================================================
function example7_compilation(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 7: Template Compilation');
    console.log('='.repeat(60));

    // Compile template once
    const emailTemplate = SDK.compile(
        'Dear {{name}},\n\n' +
        'Your order #{{order_id}} has been {{status}}.\n\n' +
        'Best regards,\n{{company}}'
    );

    // Use multiple times with different contexts
    const orders = [
        { name: 'Alice', order_id: '1001', status: 'shipped', company: 'ACME' },
        { name: 'Bob', order_id: '1002', status: 'delivered', company: 'ACME' },
        { name: 'Charlie', order_id: '1003', status: 'processing', company: 'ACME' },
    ];

    for (const order of orders) {
        const result = emailTemplate(order);
        console.log(`--- Order #${order.order_id} ---`);
        console.log(result);
        console.log();
    }
}

// =============================================================================
// Example 8: Placeholder Extraction
// =============================================================================
function example8_extraction(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 8: Placeholder Extraction');
    console.log('='.repeat(60));

    const templates = [
        'Hello {{name}}!',
        '{{user.profile.name}} works at {{company}}',
        'Items: {{items[0]}}, {{items[1]}}',
        '{{value | "default"}}',
    ];

    for (const template of templates) {
        const placeholders = SDK.extract(template);
        console.log(`Template: ${template}`);
        console.log(`  Placeholders: ${JSON.stringify(placeholders)}`);
        console.log();
    }
}

// =============================================================================
// Example 9: Validation
// =============================================================================
function example9_validation(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 9: Validation');
    console.log('='.repeat(60));

    const validTemplates = [
        '{{name}}',
        '{{user.profile.name}}',
        '{{items[0]}}',
        '{{value | "default"}}',
    ];

    const invalidTemplates = [
        '{{foo@bar}}',  // Invalid character @
        '{{foo..bar}}',  // Empty segment
    ];

    console.log('Valid templates:');
    for (const template of validTemplates) {
        try {
            SDK.validate(template);
            console.log(`  ${template}`);
        } catch (e) {
            if (e instanceof ValidationError) {
                console.log(`  ${template} - ERROR: ${e.message}`);
            }
        }
    }

    console.log('\nInvalid templates:');
    for (const template of invalidTemplates) {
        try {
            SDK.validate(template);
            console.log(`  ${template} - OK (unexpected)`);
        } catch (e) {
            if (e instanceof ValidationError) {
                console.log(`  ${template}`);
                console.log(`    Error: ${e.message}`);
            }
        }
    }
}

// =============================================================================
// Example 10: Security - Private Attribute Protection
// =============================================================================
function example10_security(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 10: Security - Private Attribute Protection');
    console.log('='.repeat(60));

    const resolver = new TemplateResolver();

    const dangerousTemplates = [
        '{{_private}}',
        '{{__proto__}}',
        '{{obj.__dict__}}',
    ];

    console.log('Attempting to access private attributes:');
    for (const template of dangerousTemplates) {
        try {
            const result = resolver.resolve(template, { _private: 'secret' }, { throwOnError: true });
            console.log(`  ${template} -> ${result}`);
        } catch (e) {
            if (e instanceof SecurityError) {
                console.log(`  ${template}`);
                console.log(`    Blocked: ${e.message}`);
            }
        }
    }
}

// =============================================================================
// Example 11: SDK Convenience Functions
// =============================================================================
function example11_sdkFunctions(): void {
    console.log('\n' + '='.repeat(60));
    console.log('Example 11: SDK Convenience Functions');
    console.log('='.repeat(60));

    const context = { name: 'World', count: 42 };

    // resolve() - single template
    const result = SDK.resolve('Hello {{name}}!', context);
    console.log(`resolve(): ${result}`);

    // resolveMany() - multiple templates
    const results = SDK.resolveMany([
        'Hello {{name}}',
        'Count: {{count}}',
        'Goodbye {{name}}'
    ], context);
    console.log(`resolveMany(): ${JSON.stringify(results)}`);

    // resolveObject() - nested objects
    const obj = { greeting: 'Hello {{name}}', data: { value: '{{count}}' } };
    const resolved = SDK.resolveObject(obj, context);
    console.log(`resolveObject(): ${JSON.stringify(resolved)}`);
}

// =============================================================================
// Main Runner
// =============================================================================
function main(): void {
    console.log('='.repeat(60));
    console.log('Runtime Template Resolver - Basic Usage Examples');
    console.log('='.repeat(60));

    example1_simpleResolution();
    example2_nestedPaths();
    example3_arrayAccess();
    example4_defaultValues();
    example5_missingStrategies();
    example6_resolveObject();
    example7_compilation();
    example8_extraction();
    example9_validation();
    example10_security();
    example11_sdkFunctions();

    console.log('\n' + '='.repeat(60));
    console.log('All examples completed!');
    console.log('='.repeat(60));
}

main();
