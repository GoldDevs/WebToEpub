from .base_parser import Parser
from .parser_factory import ParserFactory
from bs4 import BeautifulSoup

class ArchiveOfOurOwnParser(Parser):
    """
    Parser for archiveofourown.org.
    """

    def get_title(self, url: str, soup: BeautifulSoup) -> str:
        title_tag = soup.select_one("h2.heading")
        return title_tag.get_text(strip=True) if title_tag else ""

    def get_author(self, url: str, soup: BeautifulSoup) -> str:
        author_tag = soup.select_one("a[rel='author']")
        return author_tag.get_text(strip=True) if author_tag else ""

    def get_chapter_urls(self, url: str, soup: BeautifulSoup) -> list[str]:
        import re

        chapter_select = soup.select_one("select#selected_id")
        if not chapter_select:
            # Handle single-chapter works or cases where the dropdown isn't present.
            # For now, assume if no dropdown, it's a single chapter.
            # A better implementation would get the canonical URL of the work.
            return [] # Returning empty for now, will be improved.

        options = chapter_select.find_all("option")
        if not options:
            return []

        # Extract the work ID from the form action
        form = soup.select_one("ul#chapter_index form")
        action = form['action']
        match = re.search(r"/works/(\d+)/chapters", action)
        if not match:
            return [] # Could not determine work ID

        work_id = match.group(1)
        base_url = "https://archiveofourown.org"

        chapter_urls = []
        for option in options:
            chapter_id = option['value']
            chapter_url = f"{base_url}/works/{work_id}/chapters/{chapter_id}"
            chapter_urls.append(chapter_url)

        return chapter_urls

    def get_chapter_title(self, soup: BeautifulSoup) -> str:
        # TODO: Implement proper chapter title extraction for AO3
        return ""

    def extract_content(self, url: str, soup: BeautifulSoup) -> str:
        content_div = soup.select_one("div#chapters")
        if content_div:
            # The original parser has logic to remove author notes. I'll add that later.
            return str(content_div)
        return ""

# Register the parser with the factory
ParserFactory.register("archiveofourown.org", ArchiveOfOurOwnParser)
