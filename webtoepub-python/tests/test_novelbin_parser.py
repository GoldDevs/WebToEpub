import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from webtoepub.parsers.novelbin_parser import NovelbinParser

@pytest.fixture
def novelbin_soup():
    """Fixture to create a BeautifulSoup object from the test HTML file."""
    html_path = Path(__file__).parent / "testdata/novelbin_test_page.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    return BeautifulSoup(html, "html.parser")

@pytest.fixture
def novelbin_parser():
    """Fixture to create an instance of the NovelbinParser."""
    return NovelbinParser()

@pytest.mark.skip(reason="Need HTML of the main novel page to test this.")
def test_get_title(novelbin_parser, novelbin_soup):
    title = novelbin_parser.get_title("http://example.com", novelbin_soup)
    assert title == "OMG! I Transmigrated into Four Books at the Same Time!"

@pytest.mark.skip(reason="Need HTML of the main novel page to test this.")
def test_get_author(novelbin_parser, novelbin_soup):
    author = novelbin_parser.get_author("http://example.com", novelbin_soup)
    assert author == "Author Name" # Replace with actual author

def test_extract_content(novelbin_parser, novelbin_soup):
    content = novelbin_parser.extract_content("http://example.com", novelbin_soup)
    assert content is not None
    assert "Chapter 1 The Worthless Junior Sister" in content
    assert "Today's daily tasks: Greet ten people." in content

@pytest.mark.skip(reason="This requires a live network request to the AJAX endpoint.")
def test_get_chapter_urls(novelbin_parser, novelbin_soup):
    # This test would require mocking the get_html function.
    pass
