# This file is part of the Python port of the WebToEpub browser extension.
# For the original project, see: https://github.com/dteviot/WebToEpub
"""
This module contains the base Parser class.
"""
from bs4 import BeautifulSoup

class Parser:
    def __init__(self):
        pass

    def parse_index_page(self, content, url):
        self.soup = BeautifulSoup(content, 'html.parser')
        self.base_url = url

    def get_title(self):
        og_title = self.soup.select_one("meta[property='og:title']")
        if og_title and og_title.has_attr('content'):
            return og_title['content']
        if self.soup.title and self.soup.title.string:
            return self.soup.title.string
        return "Unknown Title"

    def get_author(self):
        return "Unknown Author"

    def get_cover_image_url(self):
        return None

    def get_chapter_urls(self, downloader):
        raise NotImplementedError

    def get_chapter_content(self, chapter_content, chapter_urls=None, remove_nav_links=False):
        soup = BeautifulSoup(chapter_content, 'html.parser')
        # This is a generic implementation, specific parsers can override this.
        # It tries to find a common content container.
        content_divs = ['article', 'div.chapter-content', 'div.entry-content', 'div.main-content']
        for div in content_divs:
            content = soup.select_one(div)
            if content:
                return str(self.clean_content(content, chapter_urls, remove_nav_links))
        return chapter_content # fallback

    def get_chapter_title(self, chapter_content):
        soup = BeautifulSoup(chapter_content, 'html.parser')
        if soup.title and soup.title.string:
            return soup.title.string
        return ""

    def clean_content(self, element, chapter_urls=None, remove_nav_links=False):
        """
        Removes unwanted tags and attributes from the chapter content.
        """
        if remove_nav_links and chapter_urls:
            self.remove_nav_links(element, chapter_urls)

        # Add more tags to this list as needed
        tags_to_remove = ['script', 'style', 'ins', 'iframe']
        for tag in element.find_all(tags_to_remove):
            tag.decompose()

        # Add more attributes to this list as needed
        attributes_to_remove = ['class', 'id', 'style', 'onclick', 'onmouseover']
        for tag in element.find_all(True):
            for attr in attributes_to_remove:
                if tag.has_attr(attr):
                    del tag[attr]

        return element

    def remove_nav_links(self, element, chapter_urls):
        """
        Removes links to other chapters in the book.
        """
        from urllib.parse import urljoin

        for link in element.find_all('a', href=True):
            abs_url = urljoin(self.base_url, link['href'])
            if abs_url in chapter_urls:
                link.decompose() # Removes the link and its content
