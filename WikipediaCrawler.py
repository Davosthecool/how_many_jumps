import json
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests, logging

from WikipediaPage import WikipediaPage
from WikipediaDatabase import WikipediaDatabase


class WikipediaCrawler:
    """
    A class to crawl Wikipedia pages and extract links.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='wikipedia_crawler.log', filemode='a')
    logger = logging.getLogger(__name__)

    @classmethod
    def _validate_url(cls, url: str) -> bool:
        """Validate the URL format."""
        if not url.__contains__('.wikipedia.org/'): return False

        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except AttributeError:
            return False

    @classmethod
    def crawl(cls, url: str) -> list:
        """
        Crawls the given URL and extracts links.

        :param url: The URL to crawl.
        """
        if not cls._validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        page = WikipediaPage(url)
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a',href=True):
                full_url = urljoin(response.url, link['href'])
                normalized_url = WikipediaPage(full_url).url
                if cls._validate_url(normalized_url):
                    page.children.add(normalized_url)
        except requests.RequestException as e:
            cls.logger.error(f"Request failed: {e}")
            print(f"Request failed: {e}")

        return list(set(page.children))

    @classmethod
    async def deep_crawl(cls, url: str, memo: dict[str, WikipediaPage] = None, database_handler: WikipediaDatabase = None, max_depth: int = None) -> dict[str, WikipediaPage]:
        """
        Deep crawl from the given URL, exploring links up to a specified depth.
        """
        if memo is None:
            memo: dict[str, WikipediaPage] = {}

        visiting = set()

        async def dfs(current_url: str, current_depth):
            
            if max_depth is not None and current_depth >= max_depth:
                cls.logger.debug(f"Max depth reached at {current_url}")
                memo[current_url] = WikipediaPage(current_url)
                return 0

            if current_url in visiting:
                cls.logger.debug(f"Already visiting {current_url}, skipping to avoid loop")
                return 0

            if current_url in memo and memo[current_url].depth_explored >= max_depth - current_depth:
                cls.logger.debug(f"Already explored {current_url} to depth {memo[current_url].depth_explored}, skipping")
                return memo[current_url].depth_explored

            cls.logger.info(f"Visiting: {current_url} at depth {current_depth}")
            visiting.add(current_url)
            neighbors = cls.crawl(current_url)
            cls.logger.debug(f"Found {len(neighbors)} links on {current_url}: {neighbors}")

            max_reach = 0
            for neighbor in neighbors:
                depth = await dfs(neighbor, current_depth + 1)
                max_reach = max(max_reach, 1 + depth)
            
            visiting.remove(current_url)

            page = WikipediaPage(current_url)
            page.children = neighbors
            page.depth_explored = max_reach
            memo[current_url] = page

            if database_handler:
                await database_handler.save_page(page.url, page.children, page.depth_explored)
                cls.logger.debug(f"Saved {current_url} to database")

            return max_reach

        await dfs(url, 0)
        return memo
