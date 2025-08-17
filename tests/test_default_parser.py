import unittest
import os
from src.web_to_epub.parsers.default_parser import DefaultParser

class TestDefaultParser(unittest.TestCase):

    def setUp(self):
        self.parser = DefaultParser()

        page_path = os.path.join(os.path.dirname(__file__), 'testdata', 'default_parser_page.html')

        with open(page_path, 'r', encoding='utf-8') as f:
            self.html = f.read()

        self.parser.parse_index_page(self.html, "http://www.example.com/index.html")

    def test_get_title(self):
        # The default parser should prefer the og:title
        self.assertEqual(self.parser.get_title(), "OG Default Test Page")

    def test_get_author(self):
        self.assertEqual(self.parser.get_author(), "Unknown Author")

    def test_get_cover_image_url(self):
        self.assertIsNone(self.parser.get_cover_image_url())

    def test_get_chapter_urls(self):
        # The downloader is not used by the default parser's get_chapter_urls
        chapter_urls = self.parser.get_chapter_urls(None)

        self.assertEqual(len(chapter_urls), 2)
        self.assertIn("http://www.example.com/chapter1.html", chapter_urls)
        self.assertIn("http://www.example.com/chapter2.html", chapter_urls)
        self.assertNotIn("http://www.another-domain.com/chapter3.html", chapter_urls)
        self.assertNotIn("http://www.example.com/login", chapter_urls)

    def test_get_chapter_content(self):
        # The default parser uses a generic content finder.
        # In our mock HTML, it should find the <article> tag.
        content = self.parser.get_chapter_content(self.html)
        self.assertIn("<p>This is some content.</p>", content)
        self.assertNotIn("<h1>Welcome</h1>", content) # The h1 is outside the article

if __name__ == '__main__':
    unittest.main()
