import unittest
from unittest.mock import MagicMock
from src.web_to_epub.parsers.wtr_lab_parser import WtrLabParser

class TestWtrLabParser(unittest.TestCase):

    def test_get_chapter_urls(self):
        parser = WtrLabParser()
        parser.base_url = "https://wtr-lab.com/lang/serie-123/some-slug"

        mock_downloader = MagicMock()
        mock_downloader.session.get.return_value.json.return_value = {
            "chapters": [
                {"order": 1, "title": "Chapter One", "serie_id": "s1"},
                {"order": 2, "title": "Chapter Two", "serie_id": "s1"}
            ]
        }

        chapters = parser.get_chapter_urls(mock_downloader)

        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0]['title'], "1: Chapter One")
        self.assertEqual(chapters[1]['sourceUrl'], "https://wtr-lab.com/lang/serie-123/some-slug/2")

    def test_fetch_chapter_content(self):
        parser = WtrLabParser()
        chapter_info = {
            "sourceUrl": "https://wtr-lab.com/lang/serie-123/some-slug/1",
            "title": "1: Chapter One",
            "novel_id": "123",
            "order": 1,
            "language": "lang"
        }

        mock_downloader = MagicMock()
        mock_downloader.post.return_value = {
            "chapter": {"title": "Chapter One"},
            "data": {
                "data": {
                    "body": ["This is the first paragraph.", "This is the second."]
                }
            }
        }

        content = parser.fetch_chapter_content(chapter_info, mock_downloader)

        self.assertIn("<h1>1: Chapter One</h1>", content)
        self.assertIn("<p>This is the first paragraph.</p>", content)
        self.assertIn("<p>This is the second.</p>", content)

if __name__ == '__main__':
    unittest.main()
