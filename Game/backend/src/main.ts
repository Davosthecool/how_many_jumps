import { DatabaseHelper } from './databaseHelper.ts';
import { ConfigHelper } from './configHelper.ts';
import { GraphHelper } from './graphHelper.ts';
import Fastify from "fastify";


const config = new ConfigHelper('./.env');
const DBHelper = new DatabaseHelper(config.DB_PATH);

const graphHelper = new GraphHelper();
const graph = graphHelper.createGraph(await DBHelper.getAllLinks());
console.log("Graph created.");

const app = Fastify();

app.register( async (app) => {

    app.get("/", async (request, reply) => {
        return { message: "Hello Fastify + TypeScript!" };
    });


    const distanceRequestSchema = {
        type: 'object',
        properties: {
          from: { type: 'string' },
          to: { type: 'string' },
        },
        required: ['from', 'to'],
      };
    app.post("/get_distance/", { schema: {body: distanceRequestSchema } },
    async (request, reply) => {
        const { from, to } = request.body as { from: string; to: string };
        const distance = graphHelper.findPathAndJumps(graph, from, to);
        return reply.send(distance);
    });

}, {prefix: "/api"});


const start = async () => {
  try {
    await app.listen({ port: 3000 });
    console.log("Server is running at http://localhost:3000");
  } catch (err) {
    app.log.error(err);
    console.error("Error starting the server:", err);
    process.exit(1);
  }
};

start();
