/**
 * Mount routes to the Fastify application.
 * This function is called by the server bootstrap process.
 * @param {import('fastify').FastifyInstance} server
 */
export async function mount(server) {
  server.get("/health", async (request, reply) => {
    const buildId = request.state?.build_info?.id?.trim() || "no build id found";
    return { message: "Hello from autoloaded route!", framework: "fastify", build_id: buildId };
  });
}
