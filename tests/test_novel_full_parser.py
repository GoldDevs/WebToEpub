import unittest
import os
from src.web_to_epub.parsers.novel_full_parser import NovelFullParser

class TestNovelFullParser(unittest.TestCase):

    def setUp(self):
        self.parser = NovelFullParser()

        # Load the mock HTML files
        index_path = os.path.join(os.path.dirname(__file__), 'testdata', 'novelfull_index.html')
        chapter_path = os.path.join(os.path.dirname(__file__), 'testdata', 'novelfull_chapter.html')

        with open(index_path, 'r', encoding='utf-8') as f:
            self.index_html = f.read()

        with open(chapter_path, 'r', encoding='utf-8') as f:
            self.chapter_html = f.read()

        self.parser.parse_index_page(self.index_html, "http://www.example.com/test-novel.html")

    def test_get_title(self):
        self.assertEqual(self.parser.get_title(), "Test Novel Title")

    def test_get_author(self):
        self.assertEqual(self.parser.get_author(), "Test Author")

    def test_get_cover_image_url(self):
        self.assertEqual(self.parser.get_cover_image_url(), "http://www.example.com/cover.jpg")

    def test_get_chapter_urls(self):
        # This parser needs a downloader for pagination, so we'll mock it.
        class MockDownloader:
            def __init__(self, html):
                self.html = html
            def get(self, url):
                # For this test, we don't need to return different content for page 2
                return self.html

        chapter_urls = self.parser.get_chapter_urls(MockDownloader(self.index_html))
        # The mock index has 2 chapters, and pagination up to page 2. So 2 * 2 = 4.
        self.assertEqual(len(chapter_urls), 4)
        self.assertIn("http://www.example.com/test-novel/chapter-1.html", chapter_urls)
        self.assertIn("http://www.example.com/test-novel/chapter-2.html", chapter_urls)

    def test_get_chapter_title(self):
        title = self.parser.get_chapter_title(self.chapter_html)
        self.assertEqual(title, "Chapter 1: The Beginning")

    def test_get_chapter_content_and_watermark(self):
        content = self.parser.get_chapter_content(self.chapter_html)
        self.assertIn("This is the first paragraph of the chapter.", content)
        self.assertIn("<strong>bold text</strong>", content)
        self.assertNotIn("some_annoying_watermark_text", content)

if __name__ == '__main__':
    unittest.main()
