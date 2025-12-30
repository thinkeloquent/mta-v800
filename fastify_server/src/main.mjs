import * as server from "./server.mjs";
import path from "path";
import { fileURLToPath } from 'url';

// Helper to get __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, "..");

const config = {
    title: "Fastify Integrated Server",
    port: process.env.PORT || 8080,
    bootstrap: {
        load_env: path.join(ROOT_DIR, "config/env"),
        lifecycle: path.join(ROOT_DIR, "config/lifecycle")
    }
};

try {
    // 1. Init
    const app = server.init(config);

    // 2. Start (Bootstrap + Listen)
    await server.start(app, config);

} catch (err) {
    console.error(err);
    process.exit(1);
}
