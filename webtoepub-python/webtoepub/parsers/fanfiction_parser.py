from .base_parser import Parser
from .parser_factory import ParserFactory
from bs4 import BeautifulSoup
import re

class FanFictionParser(Parser):
    """
    Parser for fanfiction.net and fictionpress.com.
    """

    def get_title(self, url: str, soup: BeautifulSoup) -> str:
        profile_top = soup.select_one("div#profile_top")
        if profile_top:
            title_tag = profile_top.select_one("b")
            if title_tag:
                return title_tag.get_text(strip=True)
        return ""

    def get_author(self, url: str, soup: BeautifulSoup) -> str:
        profile_top = soup.select_one("div#profile_top")
        if profile_top:
            author_tag = profile_top.select_one("a")
            if author_tag:
                return author_tag.get_text(strip=True)
        return ""

    def get_chapter_urls(self, url: str, soup: BeautifulSoup) -> list[str]:
        chap_select = soup.select_one("select#chap_select")
        if not chap_select:
            # Single chapter story
            return [] # Will be improved

        options = chap_select.find_all("option")
        if not options:
            return []

        onchange = chap_select.get("onchange")
        if not onchange:
            return []

        # The onchange attribute looks like:
        # "self.location.href = '/s/1234567/' + this.options[this.selectedIndex].value + '/Story-Title';"
        # We need to parse this to get the URL template.
        parts = onchange.split("'")
        if len(parts) < 4:
            return []

        url_template = parts[1]
        base_url = "https://www.fanfiction.net"

        chapter_urls = []
        for option in options:
            chapter_num = option["value"]
            chapter_url = f"{base_url}{url_template}{chapter_num}/"
            chapter_urls.append(chapter_url)

        return chapter_urls

    def extract_content(self, url: str, soup: BeautifulSoup) -> str:
        story_text = soup.select_one("div.storytext")
        return str(story_text) if story_text else ""

# Register the parser
ParserFactory.register("www.fanfiction.net", FanFictionParser)
ParserFactory.register("www.fictionpress.com", FanFictionParser)
