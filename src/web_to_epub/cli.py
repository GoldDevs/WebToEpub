"""
This module contains the command-line interface for the web-to-epub tool.
"""
import argparse
from .downloader import Downloader
from .epub_generator import EpubGenerator
from .parser_factory import get_parser

def main():
    """
    The main function for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Convert a web novel to an EPUB file.')
    parser.add_argument('url', help='The URL of the novel to convert.')
    parser.add_argument('-o', '--output', help='The output file name.')
    parser.add_argument('-d', '--default', action='store_true', help='Force the use of the default parser.')
    args = parser.parse_args()

    downloader = Downloader()
    index_page_content = downloader.get(args.url)

    if not index_page_content:
        print("Failed to download the index page. Exiting.")
        return

    parser_class = get_parser(args.url, force_default=args.default)
    if not parser_class:
        print("No parser found for the given URL. Exiting.")
        return

    parser_instance = parser_class()
    parser_instance.parse_index_page(index_page_content, args.url)

    title = parser_instance.get_title()
    if not title:
        print("Could not determine the title of the novel. Exiting.")
        return

    author = parser_instance.get_author() or "Unknown Author"

    output_filename = args.output if args.output else f"{title}.epub"

    print(f"Creating '{output_filename}' by {author}")

    epub_generator = EpubGenerator(title, author)

    cover_url = parser_instance.get_cover_image_url()
    if cover_url:
        print("Downloading cover image...")
        try:
            cover_content = downloader.session.get(cover_url, timeout=10).content
            cover_filename = cover_url.split('/')[-1]
            epub_generator.set_cover(cover_content, cover_filename)
        except Exception as e:
            print(f"Could not download cover image: {e}")

    chapter_urls = parser_instance.get_chapter_urls(downloader)
    print(f"Found {len(chapter_urls)} chapters.")

    for i, chapter_url in enumerate(chapter_urls):
        print(f"Downloading chapter {i+1}/{len(chapter_urls)}...")
        chapter_content_html = downloader.get(chapter_url)
        if chapter_content_html:
            chapter_title = parser_instance.get_chapter_title(chapter_content_html) or f"Chapter {i+1}"
            chapter_content = parser_instance.get_chapter_content(chapter_content_html)
            epub_generator.add_chapter(chapter_title, chapter_content, i+1)

    epub_generator.save(output_filename)
    print(f"Epub saved as {output_filename}")

if __name__ == '__main__':
    main()
