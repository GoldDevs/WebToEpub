# WebToEpub (Python)

This project is a Python-based command-line utility to convert web novels and other web pages into EPUB files. It is a rewrite and spiritual successor to the popular [WebToEpub browser extension](https://github.com/dteviot/WebToEpub).

The goal of this project is to provide a simple, extensible tool that can be run on any system with Python, including on mobile devices via [Termux](https://termux.com/).

## Features

-   Download web novels from supported sites.
-   Package chapters into a valid EPUB 3 file.
-   Extensible parser system to easily add support for new websites.
-   Simple command-line interface.

## Installation

You can install the package from PyPI (once it's published):

```bash
pip install webtoepub-python
```

Or, you can install it directly from the source for development:

```bash
git clone https://github.com/your-username/webtoepub-python.git
cd webtoepub-python
pip install -e .
```

## Usage

To download a web novel, simply provide the URL of the first chapter or the main table of contents page.

```bash
webtoepub "https://www.example.com/novel/story"
```

This will create an EPUB file in your current directory with a name derived from the novel's title.

You can specify a different output file name with the `--output-filename` option:

```bash
webtoepub "https://www.example.com/novel/story" --output-filename "My Awesome Novel.epub"
```

## Supported Sites

This is a new project, and the list of supported sites is growing. Currently, the following sites are supported:

-   `archiveofourown.org`
-   `fanfiction.net`
-   `fictionpress.com`
-   `novelbin.com`

We welcome contributions for new parsers! See the section below on how to add a new parser.

## How to Add a New Parser

The power of this tool comes from its extensible parser system. If you want to add support for a new website, you just need to create a new parser class. Here's how:

1.  **Create a New Parser File:**
    Create a new Python file in the `webtoepub/parsers/` directory. The filename should be descriptive, e.g., `my_new_site_parser.py`.

2.  **Create the Parser Class:**
    In your new file, create a class that inherits from `webtoepub.parsers.base_parser.Parser`.

    ```python
    from .base_parser import Parser
    from .parser_factory import ParserFactory
    from bs4 import BeautifulSoup

    class MyNewSiteParser(Parser):
        # ... implement methods here ...
    ```

3.  **Implement the Abstract Methods:**
    You must implement the four abstract methods from the `Parser` base class:
    -   `get_title(self, url: str, soup: BeautifulSoup) -> str`
    -   `get_author(self, url: str, soup: BeautifulSoup) -> str`
    -   `get_chapter_urls(self, url: str, soup: BeautifulSoup) -> list[str]`
    -   `extract_content(self, url: str, soup: BeautifulSoup) -> str`

    These methods take the URL of the page and a `BeautifulSoup` object of the parsed HTML as input. You can use `BeautifulSoup`'s methods like `select_one()` and `select()` with CSS selectors to find the required elements in the HTML.

    **Example:**
    ```python
    def get_title(self, url, soup):
        # Find the h1 tag with the class 'story_title'
        title_tag = soup.select_one("h1.story_title")
        return title_tag.get_text(strip=True) if title_tag else ""
    ```

4.  **Register Your Parser:**
    At the bottom of your parser file, you need to register your new parser with the `ParserFactory`. This tells the application which domain(s) your parser should be used for.

    ```python
    # Register the parser for 'mynewsite.com'
    ParserFactory.register("www.mynewsite.com", MyNewSiteParser)
    ```

5.  **Import Your Parser:**
    Finally, open the `webtoepub/parsers/__init__.py` file and add an import statement for your new parser. This ensures that the parser is loaded and registered when the application starts.

    ```python
    # In webtoepub/parsers/__init__.py
    from . import archiveofourown_parser
    from . import fanfiction_parser
    from . import novelbin_parser
    from . import my_new_site_parser # Add this line
    ```

6.  **Write a Test (Optional but Recommended):**
    To ensure your parser works correctly and doesn't break in the future, it's a good idea to add a test for it.
    -   Save a sample HTML file from the website to `tests/testdata/`.
    -   Create a new test file in `tests/` that uses this HTML to test your parser's methods. See `tests/test_archiveofourown_parser.py` for an example.

That's it! With these steps, you can easily extend the tool to support any website.
