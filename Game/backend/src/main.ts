import { DatabaseHelper } from './databaseHelper.ts';
import { ConfigHelper } from './configHelper.ts';
import { GraphHelper } from './graphHelper.ts';
import * as fs from 'fs';


const config = new ConfigHelper('./.env');
const DBHandler = new DatabaseHelper(config.DB_PATH);
console.log("Database path: ", config.DB_PATH);
console.log("Database handler initialized.");

const graphHelper = new GraphHelper();
const graph = graphHelper.createGraph(await DBHandler.getAllLinks())
console.log("Graph created.");

const startNode = "https://en.wikipedia.org/wiki/Martin_Luther_King";
const endNode = "https://en.wikipedia.org/wiki/Knockout";
console.log("Jumps between nodes: ", graphHelper.findPathAndJumps(graph, startNode, endNode));