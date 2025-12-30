import { init, start } from "./server.mjs";
import logger from "./logger.mjs";

const log = logger.create("main", import.meta.url);

const config = {
  title: "My API",
  host: "0.0.0.0",
  port: 3000,
  bootstrap: {
    load_env: "./config/env",
    lifecycle: "./config/lifecycle",
  },
  initial_state: {
    user: "anonymous",
    role: "guest",
  },
};

log.info("Initializing application", { title: config.title });
const server = init(config);

log.debug("Registering routes");
server.get("/", async (request) => {
  log.trace("Request received", { path: "/", requestId: request.id });
  return {
    status: "ok",
    state: request.state,
  };
});

server.get("/health", async (request) => {
  log.trace("Health check request", { path: "/health", requestId: request.id });
  return {
    status: "ok",
    state: request.state,
  };
});
log.info("Routes registered", { routes: ["/", "/health"] });

log.info("Starting server", { host: config.host, port: config.port });
await start(server, config);
