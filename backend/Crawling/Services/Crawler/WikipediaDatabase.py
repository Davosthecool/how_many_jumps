import asyncio
from datetime import datetime
import aiosqlite
import json
from contextlib import asynccontextmanager

from Services.Crawler.WikipediaPage import WikipediaPage

class WikipediaDatabase:
    def __init__(self, db_path: str, log_path: str):
        self.db_path = db_path
        self.log_path = log_path
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        await self.create_tables()

    async def create_tables(self):
        await self.conn.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            url TEXT PRIMARY KEY,
            children TEXT,
            depth_explored INTEGER
        );
        ''')
        await self.conn.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            depth INTEGER NOT NULL,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            finished_at DATETIME DEFAULT NULL,
            status TEXT NOT NULL CHECK (status IN ('queued','started', 'in_progress', 'completed', 'failed')),
            message TEXT DEFAULT NULL
        );
        ''')
        await self.conn.commit()

    async def save_page(self, url, children, depth_explored):
        await self.conn.execute('''
        INSERT OR REPLACE INTO pages (url, children, depth_explored)
        VALUES (?, ?, ?)
        ''', (url, json.dumps(list(children)), depth_explored))
        await self.conn.commit()


    async def insert_history(self, url: str, depth: int, status: str, message: str = None) -> int:
        cursor = await self.conn.execute('''
        INSERT INTO history (url, depth, status, message)
        VALUES (?, ?, ?, ?)''', (url, depth, status, message))
        await self.conn.commit()
        return cursor.lastrowid
    
    def insert_history_sync(self, url: str, depth: int, status: str, message: str = None) -> int:
        return asyncio.run(self.insert_history(url, depth, status, message))

    async def update_history(self, id: int, status: str, message: str = None, finished_at: datetime = None):
        await self.conn.execute('''
        UPDATE history
        SET status = ?, message = ?, finished_at = ?
        WHERE id = ?
        ''', (status, message, finished_at, id))
        await self.conn.commit()

    async def close(self):
        await self.conn.close()

    async def load_all_pages(self) -> dict[str, WikipediaPage]:
        cursor = await self.conn.execute('SELECT url, children, depth_explored FROM pages')
        data = await cursor.fetchall()
        pages = {}
        for url, children_json, depth in data:
            page = WikipediaPage(url)
            page.children = set(json.loads(children_json))
            page.depth_explored = depth if depth is not None else 0
            pages[url] = page
        return pages
