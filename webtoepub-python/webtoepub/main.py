import typer
from typing_extensions import Annotated
from bs4 import BeautifulSoup
from .parsers.parser_factory import ParserFactory
from .web_scraper import get_html
from .epub_writer import EpubWriter

app = typer.Typer()

@app.command()
def main(
    url: Annotated[str, typer.Argument(help="The URL of the web novel to download.")],
    output_filename: Annotated[str, typer.Option(help="The name of the output EPUB file.")] = "output.epub",
):
    """
    Downloads a web novel and converts it into an EPUB file.
    """
    print(f"Fetching web novel from: {url}")

    try:
        # Get the parser for the given URL
        parser = ParserFactory.get_parser(url)

        # Fetch the main page HTML
        main_page_html = get_html(url)
        main_page_soup = BeautifulSoup(main_page_html, "html.parser")

        # Extract metadata
        title = parser.get_title(url, main_page_soup)
        author = parser.get_author(url, main_page_soup)

        print(f"Title: {title}")
        print(f"Author: {author}")

        # Extract chapter URLs
        chapter_urls = parser.get_chapter_urls(url, main_page_soup)
        print(f"Found {len(chapter_urls)} chapters.")

        # Fetch and parse chapters
        chapters = []
        for i, chapter_url in enumerate(chapter_urls):
            print(f"Fetching chapter {i+1}: {chapter_url}")
            chapter_html = get_html(chapter_url)
            chapter_soup = BeautifulSoup(chapter_html, "html.parser")
            chapter_content = parser.extract_content(chapter_url, chapter_soup)
            chapter_title = f"Chapter {i+1}" # A more sophisticated parser could get the real title
            chapters.append({"title": chapter_title, "content": chapter_content})

        # Create the EPUB
        print("Creating EPUB file...")
        writer = EpubWriter(title=title, author=author)
        writer.write_epub(chapters, output_filename)

        print(f"EPUB file created: {output_filename}")

    except (ValueError, TypeError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    app()
