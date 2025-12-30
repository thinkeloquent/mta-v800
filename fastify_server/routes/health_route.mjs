/**
 * Mount routes to the Fastify application.
 * This function is called by the server bootstrap process.
 * @param {import('fastify').FastifyInstance} server
 */
export async function mount(server) {
  server.get("/health", async (request, reply) => {
    return { message: "Hello from autoloaded route!", framework: "fastify" };
  });
}
