from urllib.parse import urlparse


class WikipediaPage:
    def __init__(self, url: str):
        url_result = urlparse(url)
        self.url = url_result.scheme + '://' + url_result.netloc + url_result.path
        self.url_variants = set([url, self.url])
        self.children = set()
        self.depth_explored = 0

    def __str__(self):
        return f'WikipediaLink({self.url})'

    def __repr__(self):
        return f'WikipediaLink({self.url})'

    def __eq__(self, other):
        if isinstance(other, WikipediaPage):
            return self.url == other.url
        return False

    def __hash__(self):
        return hash(self.url)