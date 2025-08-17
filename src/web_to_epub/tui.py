from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Button, Input, Static, RichLog
from textual.worker import work

from .downloader import Downloader
from .epub_generator import EpubGenerator
from .parser_factory import get_parser

class WebToEpubApp(App):
    """A Textual app to convert web novels to EPUB."""

    CSS_PATH = "tui.css"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container():
            yield Input(placeholder="Enter novel URL here...", id="url_input")
            yield Button("Download", variant="primary", id="download_button")
            yield RichLog(id="logs", wrap=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "download_button":
            url = self.query_one("#url_input", Input).value
            if url:
                self.query_one("#download_button").disabled = True
                self.query_one("#logs").clear()
                self.download_novel(url)

    @work(exclusive=True)
    def download_novel(self, url: str) -> None:
        """A worker thread to download the novel."""
        log = self.query_one("#logs", RichLog)

        log.write("Starting download...")
        downloader = Downloader()
        index_page_content = downloader.get(url)

        if not index_page_content:
            log.write("Failed to download the index page. Exiting.")
            self.query_one("#download_button").disabled = False
            return

        parser_class = get_parser(url)
        if not parser_class:
            log.write("No parser found for the given URL. Using default.")
            parser_class = get_parser(url, force_default=True)

        parser_instance = parser_class()
        parser_instance.parse_index_page(index_page_content, url)

        title = parser_instance.get_title()
        if not title or title == "Unknown Title":
            log.write("Could not determine the title of the novel. Exiting.")
            self.query_one("#download_button").disabled = False
            return

        author = parser_instance.get_author()
        output_filename = f"{title}.epub"

        log.write(f"Creating '{output_filename}' by {author}")
        epub_generator = EpubGenerator(title, author)

        cover_url = parser_instance.get_cover_image_url()
        if cover_url:
            log.write("Downloading cover image...")
            try:
                cover_content = downloader.session.get(cover_url, timeout=10).content
                cover_filename = cover_url.split('/')[-1]
                epub_generator.set_cover(cover_content, cover_filename)
            except Exception as e:
                log.write(f"Could not download cover image: {e}")

        chapter_urls = parser_instance.get_chapter_urls(downloader)
        log.write(f"Found {len(chapter_urls)} chapters.")

        for i, chapter_url in enumerate(chapter_urls):
            log.write(f"Downloading chapter {i+1}/{len(chapter_urls)}...")
            self.call_from_thread(log.refresh) # Refresh the log
            chapter_content_html = downloader.get(chapter_url)
            if chapter_content_html:
                chapter_title = parser_instance.get_chapter_title(chapter_content_html) or f"Chapter {i+1}"
                chapter_content = parser_instance.get_chapter_content(chapter_content_html)
                epub_generator.add_chapter(chapter_title, chapter_content, i+1)

        epub_generator.save(output_filename)
        log.write(f"Epub saved as {output_filename}")
        self.query_one("#download_button").disabled = False


def main():
    """Run the Textual app."""
    app = WebToEpubApp()
    app.run()

if __name__ == "__main__":
    main()
