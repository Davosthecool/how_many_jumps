import requests, asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from WikipediaCrawler import WikipediaCrawler
from WikipediaDatabase import WikipediaDatabase

async def main():
    db = WikipediaDatabase('wikipedia_crawl.db')
    print("Connecting...")
    await db.connect()
    print("Loading pages...")
    pages = await db.load_all_pages()
    print("Crawling...")
    await WikipediaCrawler.deep_crawl('https://en.wikipedia.org/wiki/Martin_Luther_King', pages, db, 3)
    print("Closing Connection...")
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())