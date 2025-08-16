from .base_parser import Parser
from bs4 import BeautifulSoup

class NovelfullParser(Parser):
    """
    Base parser for sites that use the Novelfull template.
    """

    def get_title(self, url: str, soup: BeautifulSoup) -> str:
        title_tag = soup.select_one("h3.title")
        return title_tag.get_text(strip=True) if title_tag else ""

    def get_author(self, url: str, soup: BeautifulSoup) -> str:
        author_link = soup.select_one("ul.info-meta li a")
        return author_link.get_text(strip=True) if author_link else ""

    def get_chapter_urls(self, url: str, soup: BeautifulSoup) -> list[str]:
        # This will be overridden by subclasses.
        # The base Novelfull parser has complex pagination logic for the TOC.
        # I will not implement this for now.
        return []

    def get_chapter_title(self, soup: BeautifulSoup) -> str:
        # Default implementation for Novelfull-based sites
        title_tag = soup.select_one(".chr-text")
        return title_tag.get_text(strip=True) if title_tag else ""

    def extract_content(self, url: str, soup: BeautifulSoup) -> str:
        content_div = soup.select_one("#chr-content, #chapter-content")
        return str(content_div) if content_div else ""
