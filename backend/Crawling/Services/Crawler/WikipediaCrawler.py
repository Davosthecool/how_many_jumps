import time
from typing import Any
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests, logging

from Services.Crawler.WikipediaPage import WikipediaPage
from Services.Crawler.WikipediaDatabase import WikipediaDatabase


class WikipediaCrawler:
    """
    A class to crawl Wikipedia pages and extract links.
    """

    def __init__(self, log_path: str):
        """
        Initialize the WikipediaCrawler with a log path.
        """
        logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    @classmethod
    def _validate_url(self, url: str, domain_prefix: str = '') -> bool:
        """Validate the URL format."""
        if not domain_prefix+'.wikipedia.org' in url: 
            raise ValueError(f"URL {url} does not contain the domain prefix: {domain_prefix}.wikipedia.org")

        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except AttributeError:
            raise ValueError(f"Invalid URL: {url}")

    def crawl(self, url: str, domain_prefix: str ='') -> list:
        """
        Crawls the given URL and extracts links.

        :param url: The URL to crawl.
        """
        try:
            if not self._validate_url(url, domain_prefix):
                raise ValueError(f"Invalid URL: {url}")
        except ValueError as e:
            self.logger.error(f"Validation failed: {e}")
            raise ValueError(f"Validation failed: {e}")
        
        page = WikipediaPage(url)
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a',href=True):
                full_url = urljoin(response.url, link['href'])
                normalized_url = WikipediaPage(full_url).url
                try:
                    if self._validate_url(normalized_url, domain_prefix):
                        page.children.add(normalized_url)
                except ValueError:
                    self.logger.debug(f"Invalid URL found: {normalized_url}, skipping")
                    continue
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            print(f"Request failed: {e}")

        return list(set(page.children))

    async def deep_crawl(self, url: str, memo: dict[str, WikipediaPage] = None, database_handler: WikipediaDatabase = None, max_depth: int = None) -> dict[str, Any]:
        """
        Deep crawl from the given URL, exploring links up to a specified depth.
        """

        if memo is None:
            memo: dict[str, WikipediaPage] = {}

        visiting = set()

        domain = urlparse(url).netloc.split('.')[0]
        if domain == 'wikipedia':
            domain = ''

        start_time = time.time()
        start_memory = len(memo)
        self.logger.info(f"\n\nStarting deep crawl from {url} with domain {domain}")
        self.logger.info(f"Max depth: {max_depth}\n\n")

        async def dfs(current_url: str, current_depth):
            
            if max_depth is not None and current_depth >= max_depth:
                self.logger.debug(f"Max depth reached at {current_url}")
                memo[current_url] = WikipediaPage(current_url)
                return 0

            if current_url in visiting:
                self.logger.debug(f"Already visiting {current_url}, skipping to avoid loop")
                return 0

            if current_url in memo and memo[current_url].depth_explored >= max_depth - current_depth:
                self.logger.debug(f"Already explored {current_url} to depth {memo[current_url].depth_explored}, skipping")
                return memo[current_url].depth_explored

            self.logger.info(f"Visiting: {current_url} at depth {current_depth}")
            visiting.add(current_url)
            try:
                neighbors = self.crawl(current_url, domain)
            except ValueError as e:
                self.logger.error(f"Error crawling {current_url}: {e}")
                return 0
            self.logger.info(f"Found {len(neighbors)} links")

            max_reach = 0
            for i,neighbor in enumerate(neighbors):
                self.logger.debug(f"Entering link {i+1}/{len(neighbors)}")
                depth = await dfs(neighbor, current_depth + 1)
                max_reach = max(max_reach, 1 + depth)
            
            visiting.remove(current_url)

            page = WikipediaPage(current_url)
            page.children = neighbors
            page.depth_explored = max_reach
            memo[current_url] = page

            if database_handler:
                await database_handler.save_page(page.url, page.children, page.depth_explored)
                self.logger.debug(f"Saved {current_url} to database")

            return max_reach

        await dfs(url, 0)

        dict_result = {
            "visited": len(memo) - start_memory,
            "total": len(memo),
            
            "start_url": url,
            "domain": domain,
            "depth": max_depth,

            "started_at": start_time,
            "finished_at": time.time(),
            "duration": time.time() - start_time,
        }
        
        self.logger.info(f"Deep crawl completed in {dict_result['duration']:.2f} seconds")
        self.logger.info(f"Visited {dict_result['visited']} pages")

        return dict_result
