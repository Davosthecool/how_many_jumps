import { DatabaseHelper } from './databaseHelper.ts';
import { ConfigHelper } from './configHelper.ts';
import { GraphHelper } from './graphHelper.ts';
import Fastify from "fastify";
import cors from '@fastify/cors';


const app = Fastify({logger: {
    level: 'info',
    transport: {
        target: 'pino-pretty',
        options: {
            colorize: true,
            translateTime: 'SYS:standard',
            ignore: 'pid,hostname'
        }
    }
}});

const config = new ConfigHelper('./.env');
app.log.info("Config loaded: " + JSON.stringify(config));
const DBHelper = new DatabaseHelper(config.DB_PATH);
app.log.info("DatabaseHelper initialized");
const graphHelper = new GraphHelper();
const graph = graphHelper.createGraph(await DBHelper.getAllLinks());
app.log.info("Graph created with nodes: " + graph.nodes().length + " and edges: " + graph.edges().length);

await app.register(cors, {
  origin: 'http://127.0.0.1:3001'
});

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
  } catch (err) {
    app.log.error(err);
    console.error("Error starting the server:", err);
    process.exit(1);
  }
};

start();
