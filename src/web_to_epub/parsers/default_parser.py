"""
This module contains the DefaultParser class.
"""
from urllib.parse import urljoin, urlparse
from ..parser import Parser

class DefaultParser(Parser):
    def get_chapter_urls(self, downloader):
        """
        A default implementation that tries to find all links on the page
        that point to the same domain.
        """
        urls = []
        base_domain = urlparse(self.base_url).netloc

        for link in self.soup.find_all('a', href=True):
            href = link['href']

            # Make the URL absolute
            abs_url = urljoin(self.base_url, href)

            # Check if the link is on the same domain
            if urlparse(abs_url).netloc == base_domain:
                # Add some basic filtering to avoid common non-chapter links
                if not any(x in href for x in ['login', 'register', 'search', '#']):
                    urls.append(abs_url)

        # Remove duplicates while preserving order
        return list(dict.fromkeys(urls))
