import * as server from "@internal/polyglot-server";
import path from "path";
import { fileURLToPath } from "url";
import { printRoutes } from "./print_routes.mjs";

// Helper to get __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, "..");

const config = {
  title: "Fastify Integrated Server",
  port: process.env.PORT || 8080,
  bootstrap: {
    load_env: path.join(ROOT_DIR, "config/environment"),
    lifecycle: path.join(ROOT_DIR, "config/lifecycle"),
    routes: path.join(ROOT_DIR, "routes"),
  },
  initial_state: {
    build_info: {
      build_id: process.env.BUILD_ID || "",
      build_version: process.env.BUILD_VERSION || "",
      app_env: process.env.APP_ENV || "",
      id: `${process.env.BUILD_ID || ""} ${process.env.BUILD_VERSION || ""} ${process.env.APP_ENV || ""}`,
    },
  },
};

try {
  // 1. Init
  const app = server.init(config);

  // 2. Start (Bootstrap + Listen)
  await server.start(app, config);

  // 3. Print routes after server is ready
  await app.ready();
  printRoutes(app);
} catch (err) {
  console.error(err);
  process.exit(1);
}
