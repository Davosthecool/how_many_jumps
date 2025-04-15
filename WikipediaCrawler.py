import json
from urllib.parse import urlparse
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
        if not url.__contains__('wikipedia.org'): return False

        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except AttributeError:
            return False

    @classmethod
    def crawl(cls, url: str) -> WikipediaPage:
        """
        Crawls the given URL and extracts links.

        :param url: The URL to crawl.
        """
        if not cls._validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        page = WikipediaPage(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            if link.get('href') and cls._validate_url(link.get('href')):
                page.children.add(link.get('href'))
        return page

    @classmethod
    async def deep_crawl(cls, url: str, max_depth: int = 2, db_path='wikipedia_crawl.db'):
        cls.logger.info(f'Starting deep crawl from {url} with max depth {max_depth}')

        # Connexion DB
        db = WikipediaDatabase(db_path)
        await db.connect()

        # Chargement des données existantes
        cls.logger.info('Loading existing pages from database...')
        page_map = await db.load_all_pages()

        to_visit = [(url, 0)]

        while to_visit:
            current_url, depth = to_visit.pop(0)
            base_url = WikipediaPage(current_url).url
            current_page = page_map.get(base_url)

            # Calcul de profondeur restante à explorer à partir de cette page
            depth_remaining = max_depth - depth
            if current_page and current_page.depth_explored >= depth_remaining:
                cls.logger.info(f'Skipping {base_url} at depth {depth} (already explored {current_page.depth_explored} deep)')
                continue

            cls.logger.info(f'Visiting: {base_url} at depth {depth}')
            try:
                page = cls.crawl(current_url)
                if current_page is None:
                    current_page = WikipediaPage(base_url)

                # Nettoyage des liens enfants
                current_page.children = {WikipediaPage(child).url for child in page.children}

                # Mise à jour de la profondeur explorée
                current_page.depth_explored = max(current_page.depth_explored, 1)

                # Traitement des enfants
                for child_url in current_page.children:
                    if child_url not in page_map:
                        page_map[child_url] = WikipediaPage(child_url)
                    page_map[child_url].parents.add(base_url)

                    if depth + 1 <= max_depth:
                        to_visit.append((child_url, depth + 1))

                # Enregistrement
                page_map[base_url] = current_page
                cls.logger.info(f'Saving {base_url} to database...')
                db.save_page(base_url, current_page.children, current_page.parents, current_page.depth_explored)

            except ValueError as e:
                print(f"Error crawling {current_url}: {e}")
                cls.logger.error(f"Error crawling {current_url}: {e}")

        await db.close()

