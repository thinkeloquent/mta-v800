import { init, start } from "./server.mjs";

const config = {
    title: "My API",
    host: "0.0.0.0",
    port: 3000,
    bootstrap: {
        load_env: "./config/env",
        lifecycle: "./config/lifecycle"
    },
    initial_state: {
        user: "anonymous",
        role: "guest"
    }
};

const server = init(config);

server.get("/health", async (request) => ({ status: "ok", state: request.state }));

console.log(`Starting server on ${config.host}:${config.port}...`);
await start(server, config);
