import sqlite3 from 'sqlite3';

export class DatabasePage {
    public url: string;
    public children: Array<string>;
    public depth: number;

    constructor(url: string, children: string, depth: number) {
        this.url = url;
        this.children = JSON.parse(children);
        this.depth = depth;
    }
}

export class DatabaseHelper{
    private db: sqlite3.Database;

    constructor(dbPath: string) {
        this.db = new sqlite3.Database(dbPath, (err) => {
            if (err) {
                throw new Error('Error opening database ' + err.message);
            }
        });
    }

    public close() {
        this.db.close((err) => {
            if (err) {
                throw new Error('Error closing database ' + err.message);
            }
        });
    }

    private deserialize_row(row: { url: string; children: string; depth_explored: number }): DatabasePage {
        return new DatabasePage(row.url, row.children, row.depth_explored);
    }

    public getOneLink(link: string): Promise<DatabasePage | null> {
        return new Promise((resolve, reject) => {
            this.db.get("SELECT * FROM pages WHERE url = ?", [link], (err, row: { url: string; children: string; depth_explored: number } | undefined) => {
                if (err) {
                    throw new Error('Error fetching link ' + err.message);
                    reject(err);
                } else if (row) {
                    resolve(this.deserialize_row(row));
                } else {
                    resolve(null); // No row found
                }
            });
        });
    }
    
    public getAllLinks(): Promise<DatabasePage[]> {
        return new Promise((resolve, reject) => {
            this.db.all("SELECT * FROM pages", [], (err, rows: Array<{ url: string; children: string; depth_explored: number }>) => {
                if (err) {
                    throw new Error('Error fetching link ' + err.message);
                    reject(err);
                } else {
                    resolve(rows.map(row => this.deserialize_row(row)));
                }
            });
        });
    }

    public getParentLinks(link: string): Promise<DatabasePage[]> {
        return new Promise((resolve, reject) => {
            this.db.all("SELECT * FROM pages WHERE children LIKE ?", [`%"${link}"%`], (err, rows: Array<{ url: string; children: string; depth_explored: number }>) => {
                if (err) {
                    throw new Error('Error fetching link ' + err.message);
                    reject(err);
                } else {
                    resolve(rows.map(row => this.deserialize_row(row)));
                }
            });
        });
    }
}