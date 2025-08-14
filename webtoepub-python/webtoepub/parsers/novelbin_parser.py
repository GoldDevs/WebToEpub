from .novelfull_parser import NovelfullParser
from .parser_factory import ParserFactory
from ..web_scraper import get_html
from bs4 import BeautifulSoup

class NovelbinParser(NovelfullParser):
    """
    Parser for novelbin.com.
    """

    def get_chapter_urls(self, url: str, soup: BeautifulSoup) -> list[str]:
        # This parser uses an AJAX call to get the chapter list.
        slug = url.strip("/").split("/")[-1]
        ajax_url = f"https://novelbin.com/ajax/chapter-archive?novelId={slug}"

        try:
            ajax_html = get_html(ajax_url)
            ajax_soup = BeautifulSoup(ajax_html, "html.parser")

            chapter_links = ajax_soup.select("ul.list-chapter a")
            return [a["href"] for a in chapter_links]
        except Exception as e:
            print(f"Could not fetch chapter list from {ajax_url}: {e}")
            return []

# Register the parser
ParserFactory.register("novelbin.com", NovelbinParser)
