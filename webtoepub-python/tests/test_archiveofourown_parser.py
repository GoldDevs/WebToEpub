import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from webtoepub.parsers.archiveofourown_parser import ArchiveOfOurOwnParser

@pytest.fixture
def ao3_soup():
    """Fixture to create a BeautifulSoup object from the test HTML file."""
    html_path = Path(__file__).parent / "testdata/ao3_test_page.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    return BeautifulSoup(html, "html.parser")

@pytest.fixture
def ao3_parser():
    """Fixture to create an instance of the ArchiveOfOurOwnParser."""
    return ArchiveOfOurOwnParser()

def test_get_title(ao3_parser, ao3_soup):
    title = ao3_parser.get_title("http://example.com", ao3_soup)
    assert title == "Miku's Adventures - Spring Summer?"

def test_get_author(ao3_parser, ao3_soup):
    author = ao3_parser.get_author("http://example.com", ao3_soup)
    assert author == "fiogutz"

def test_extract_content(ao3_parser, ao3_soup):
    content = ao3_parser.extract_content("http://example.com", ao3_soup)
    assert content is not None
    assert "Chapter Text" in content
    assert "[tv opening type thing, then we see Mr Tumble and Tophat (The Nightly Manor) standing.]" in content

def test_get_chapter_urls(ao3_parser, ao3_soup):
    # This test will initially fail because the parser logic is incomplete.
    # I will use this test to drive the implementation.
    chapter_urls = ao3_parser.get_chapter_urls("http://example.com", ao3_soup)

    # Based on the HTML, there is a dropdown with chapter links.
    # The parser should be able to find these.
    # The select element has options with values like "167336866", "177681721", etc.
    # These are chapter IDs. The full URL is /works/65073223/chapters/<chapter_id>

    # The current implementation looks for `ol.chapter a`, which is not present on this page for the full list.
    # The dropdown is inside `ul#chapter_index select`.

    assert len(chapter_urls) == 4
    base_url = "https://archiveofourown.org"
    assert chapter_urls[0] == base_url + "/works/65073223/chapters/167336866"
    assert chapter_urls[1] == base_url + "/works/65073223/chapters/177681721"
    assert chapter_urls[2] == base_url + "/works/65073223/chapters/177683526"
    assert chapter_urls[3] == base_url + "/works/65073223/chapters/178774731"
