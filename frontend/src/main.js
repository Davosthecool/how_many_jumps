import Fastify from 'fastify';
import fastifyStatic from '@fastify/static';
import fastifyCors from '@fastify/cors';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// __dirname équivalent en ESModules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = Fastify({
    logger: {
        level: 'info',
        transport: {
            target: 'pino-pretty',
            options: {
                colorize: true,
                translateTime: 'SYS:standard',
                ignore: 'pid,hostname'
            }
        }
    }
});

app.register(fastifyCors, {
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
});

app.register(fastifyStatic, {
    root: join(__dirname, '../public'),
    wildcard: false,
});

app.get('/*', async (request, reply) => {
    reply.type('text/html').sendFile('index.html');
});

app.listen({ port: 3001 }, (err, address) => {
    if (err) {
        app.log.error(err);
        process.exit(1);
    }
});
