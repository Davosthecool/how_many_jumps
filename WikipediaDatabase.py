import aiosqlite
import json
from contextlib import asynccontextmanager

from WikipediaPage import WikipediaPage

class WikipediaDatabase:
    def __init__(self, db_path='wikipedia_crawl.db'):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        await self.create_table()

    @asynccontextmanager
    async def use_db(path='wikipedia_crawl.db'):
        db = WikipediaDatabase(path)
        await db.connect()
        try:
            yield db
        finally:
            await db.close()

    async def create_table(self):
        await self.conn.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            url TEXT PRIMARY KEY,
            children TEXT,
            depth_explored INTEGER
        )
        ''')
        await self.conn.commit()

    async def save_page(self, url, children, depth_explored):
        await self.conn.execute('''
        INSERT OR REPLACE INTO pages (url, children, depth_explored)
        VALUES (?, ?, ?)
        ''', (url, json.dumps(list(children)), depth_explored))
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
