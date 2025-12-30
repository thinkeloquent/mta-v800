/**
 * Logger utility for defensive programming with verbose logging.
 *
 * Usage:
 *   import logger from "./logger.mjs";
 *   const log = logger.create("server", import.meta.url);
 *   log.info("Server started");
 *   log.debug("Request received", { method: "GET", path: "/" });
 *   log.error("Failed to connect", new Error("Connection refused"));
 */

import path from "path";

// Log levels with numeric priority (lower = more important)
const LOG_LEVELS = {
    error: 0,
    warn: 1,
    info: 2,
    debug: 3,
    trace: 4,
};

// ANSI color codes for terminal output
const COLORS = {
    reset: "\x1b[0m",
    red: "\x1b[31m",
    yellow: "\x1b[33m",
    blue: "\x1b[34m",
    cyan: "\x1b[36m",
    gray: "\x1b[90m",
    white: "\x1b[37m",
};

const LEVEL_COLORS = {
    error: COLORS.red,
    warn: COLORS.yellow,
    info: COLORS.blue,
    debug: COLORS.cyan,
    trace: COLORS.gray,
};

// Default configuration
const DEFAULT_CONFIG = {
    level: process.env.LOG_LEVEL || "debug",
    colorize: process.env.NO_COLOR !== "1",
    timestamp: true,
    json: process.env.LOG_FORMAT === "json",
    // Custom output function (defaults to console)
    output: null,
};

/**
 * Extract filename from import.meta.url or __filename
 * @param {string} fileUrl - The file URL or path
 * @returns {string} - Extracted filename
 */
function extractFilename(fileUrl) {
    if (!fileUrl) return "unknown";

    // Handle import.meta.url (file:// URLs)
    if (fileUrl.startsWith("file://")) {
        const url = new URL(fileUrl);
        return path.basename(url.pathname);
    }

    // Handle regular paths
    return path.basename(fileUrl);
}

/**
 * Format a log entry for human-readable output
 */
function formatHuman(entry, config) {
    const { timestamp, level, package: pkg, filename, message, data, error } = entry;
    const levelColor = config.colorize ? LEVEL_COLORS[level] : "";
    const resetColor = config.colorize ? COLORS.reset : "";
    const grayColor = config.colorize ? COLORS.gray : "";

    let line = "";

    // Timestamp
    if (config.timestamp) {
        line += `${grayColor}[${timestamp}]${resetColor} `;
    }

    // Level (padded)
    const levelStr = level.toUpperCase().padEnd(5);
    line += `${levelColor}${levelStr}${resetColor} `;

    // Package and filename context
    line += `${grayColor}[${pkg}:${filename}]${resetColor} `;

    // Message
    line += message;

    // Additional data
    if (data && Object.keys(data).length > 0) {
        line += ` ${grayColor}${JSON.stringify(data)}${resetColor}`;
    }

    // Error stack
    if (error) {
        line += `\n${COLORS.red}${error.stack || error}${resetColor}`;
    }

    return line;
}

/**
 * Format a log entry as JSON
 */
function formatJson(entry) {
    return JSON.stringify({
        ...entry,
        error: entry.error ? {
            message: entry.error.message,
            stack: entry.error.stack,
            name: entry.error.name,
        } : undefined,
    });
}

/**
 * Create a logger instance for a specific package/module.
 *
 * @param {string} packageName - The name of the package/module
 * @param {string} filename - The filename (use import.meta.url or __filename)
 * @param {object} [options] - Optional configuration overrides
 * @returns {object} - Logger instance with standard Console interface
 */
function create(packageName, filename, options = {}) {
    const config = { ...DEFAULT_CONFIG, ...options };
    const currentLevelPriority = LOG_LEVELS[config.level] ?? LOG_LEVELS.info;
    const extractedFilename = extractFilename(filename);

    // Custom output or default console
    const output = config.output || {
        log: console.log,
        error: console.error,
    };

    /**
     * Internal log function
     */
    function logAtLevel(level, message, dataOrError, maybeError) {
        const levelPriority = LOG_LEVELS[level];

        // Skip if below current log level
        if (levelPriority > currentLevelPriority) {
            return;
        }

        // Parse arguments - support (message), (message, data), (message, error), (message, data, error)
        let data = {};
        let error = null;

        if (dataOrError instanceof Error) {
            error = dataOrError;
        } else if (dataOrError && typeof dataOrError === "object") {
            data = dataOrError;
            if (maybeError instanceof Error) {
                error = maybeError;
            }
        }

        const entry = {
            timestamp: new Date().toISOString(),
            level,
            package: packageName,
            filename: extractedFilename,
            message: String(message),
            data: Object.keys(data).length > 0 ? data : undefined,
            error: error || undefined,
        };

        // Format output
        const formatted = config.json ? formatJson(entry) : formatHuman(entry, config);

        // Write to output
        if (level === "error" || level === "warn") {
            output.error(formatted);
        } else {
            output.log(formatted);
        }
    }

    // Create logger instance with Console-like interface
    const logger = {
        // Standard Console methods
        log: (message, data, error) => logAtLevel("info", message, data, error),
        info: (message, data, error) => logAtLevel("info", message, data, error),
        warn: (message, data, error) => logAtLevel("warn", message, data, error),
        error: (message, data, error) => logAtLevel("error", message, data, error),
        debug: (message, data, error) => logAtLevel("debug", message, data, error),
        trace: (message, data, error) => logAtLevel("trace", message, data, error),

        // Metadata
        packageName,
        filename: extractedFilename,
        level: config.level,

        // Create child logger with same package but different filename or config
        child: (childFilename, childOptions = {}) => {
            return create(packageName, childFilename, { ...config, ...childOptions });
        },

        // Create new logger with additional context in data
        withContext: (context) => {
            const contextLogger = {};
            for (const method of ["log", "info", "warn", "error", "debug", "trace"]) {
                contextLogger[method] = (message, data = {}, error) => {
                    logger[method](message, { ...context, ...data }, error);
                };
            }
            return contextLogger;
        },
    };

    return logger;
}

// Export the logger factory
const logger = {
    create,
    LOG_LEVELS,
    DEFAULT_CONFIG,
};

export default logger;
export { create, LOG_LEVELS };
