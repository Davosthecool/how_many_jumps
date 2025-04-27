import { Graph } from "@dagrejs/graphlib";
import { DatabasePage } from "./databaseHelper.ts";

export class GraphHelper {

    private addNode(graph: Graph, node: DatabasePage): void {
        try {
            if (!graph.hasNode(node.url)) {
                graph.setNode(node.url, node);
            }
        } catch (error) {
            console.error(`Error adding node ${node.url}: ${error}`);
        }
    }

    private addEdge(graph: Graph, fromNode: string, toNode: string): void {
        if (!graph.hasEdge(fromNode, toNode)) {
            graph.setEdge(fromNode, toNode);
        }
    }

    public findPathAndJumps(graph: Graph, startNode: string, endNode: string): { pathExists: boolean, jumps: number } {
        const visited = new Set<string>();
        const queue: { node: string, jumps: number }[] = [{ node: startNode, jumps: 0 }];
        
        while (queue.length > 0) {
            const current = queue.shift()!;
            const currentNode = current.node;
            const currentJumps = current.jumps;
            
            if (currentNode === endNode) {
                return { pathExists: true, jumps: currentJumps };
            }

            if (!visited.has(currentNode)) {
                visited.add(currentNode);

                const successors = graph.successors(currentNode);
                if (Array.isArray(successors)) {
                    for (const successor of successors) {
                        queue.push({ node: successor, jumps: currentJumps + 1 });
                    }
                }
            }
        }

        return { pathExists: false, jumps: -1 };
    }


    public createGraph(pages: DatabasePage[]): Graph {
        const graph = new Graph({ directed: true });
        for (const page of pages) {
            this.addNode(graph, page);
        }

        for (const page of pages) {
            for (const child of page.children) {
                try {
                    if (!graph.hasNode(child)) {
                        this.addNode(graph, new DatabasePage(child, '[]', 0));
                    }
                    this.addEdge(graph, page.url, child);
                } catch (error) {
                    console.error(`Error adding edge from ${page.url} to ${child}: ${error}`);
                }
            }
        }

        return graph;
    }

    public generateDOT(graph: Graph): string {
        let dot = 'digraph G {\n';

        for (const edgeObj of graph.edges()) {
            const { v: from, w: to } = edgeObj;
            dot += `    "${from}" -> "${to}"\n`;
        }

        dot += '}';
        return dot;
    }
}
