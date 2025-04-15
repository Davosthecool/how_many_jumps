import requests, asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from WikipediaCrawler import WikipediaCrawler

async def main():
    await WikipediaCrawler.deep_crawl('https://en.wikipedia.org/wiki/Martin_Luther_King', 5)

if __name__ == "__main__":
    asyncio.run(main())