"""
This module contains the WtrLabParser class.
"""
import json
import re
from ..parser import Parser

class WtrLabParser(Parser):

    API_BASED = True # Flag for the TUI to know how to handle this parser

    def get_title(self):
        return self.soup.select_one("h1").get_text()

    def get_author(self):
        # This info is not on the main page, would require another API call.
        # Sticking to Unknown for now.
        return "Unknown Author"

    def get_cover_image_url(self):
        img_tag = self.soup.select_one(".image-wrap img")
        return img_tag['src'] if img_tag else None

    def get_chapter_urls(self, downloader):
        leaves = self.base_url.split("/")
        language = leaves[3]
        id_part = leaves[4]
        self.slug = leaves[5].split("?")[0]

        match = re.search(r'(\d+)', id_part)
        if not match:
            return []

        novel_id = match.group(1)

        api_url = f"https://wtr-lab.com/api/chapters/{novel_id}"
        chapters_data = downloader.session.get(api_url).json()

        return [{
            "sourceUrl": f"https://wtr-lab.com/{language}/serie-{novel_id}/{self.slug}/{chapter['order']}",
            "title": f"{chapter['order']}: {chapter['title']}",
            "novel_id": novel_id,
            "order": chapter['order'],
            "language": language
        } for chapter in chapters_data.get("chapters", [])]

    def fetch_chapter_content(self, chapter_info, downloader):
        """
        Fetches chapter content from the API. chapter_info is a dict from get_chapter_urls.
        """
        api_url = "https://wtr-lab.com/api/reader/get"
        payload = {
            "translate": "web", # Hardcoded for now
            "language": chapter_info['language'],
            "raw_id": chapter_info['novel_id'],
            "chapter_no": str(chapter_info['order']),
            "retry": False,
            "force_retry": False
        }

        chapter_data = downloader.post(api_url, data=payload)
        return self._build_chapter_html(chapter_data, chapter_info)

    def _build_chapter_html(self, chapter_data, chapter_info):
        """
        Constructs an HTML string for the chapter from the API response.
        """
        if not chapter_data or not chapter_data.get("data", {}).get("data", {}).get("body"):
            return ""

        title = f"<h1>{chapter_info['order']}: {chapter_data['chapter']['title']}</h1>"
        body_paragraphs = [f"<p>{p}</p>" for p in chapter_data['data']['data']['body']]

        # Simple term replacement, ignoring the glossary for now
        body_html = "".join(body_paragraphs)

        return f"<html><head><title>{chapter_info['title']}</title></head><body>{title}{body_html}</body></html>"
