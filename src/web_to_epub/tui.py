from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Input, Static, RichLog, TextArea, Checkbox
from textual.worker import work
from textual.screen import Screen

from .downloader import Downloader
from .epub_generator import EpubGenerator
from .parser_factory import get_parser

class SettingsScreen(Screen):
    """A screen to manage advanced settings."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Checkbox("Skip images", id="skip_images", value=self.app.skip_images)
            yield Checkbox("Create EPUB 3", id="epub3", value=self.app.epub3)
            yield Static("Series:", classes="label")
            yield Input(id="series_name", value=self.app.series_name or "")
            yield Static("Volume:", classes="label")
            yield Input(id="series_index", value=self.app.series_index or "")
            yield Static("Custom Stylesheet:", classes="label")
            yield TextArea(self.app.custom_stylesheet or "", id="stylesheet_input", language="css")
            with Horizontal(classes="button-bar"):
                yield Button("Save", variant="primary", id="save_settings")
                yield Button("Back", id="back_to_main")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_settings":
            self.app.skip_images = self.query_one("#skip_images", Checkbox).value
            self.app.epub3 = self.query_one("#epub3", Checkbox).value
            self.app.series_name = self.query_one("#series_name", Input).value
            self.app.series_index = self.query_one("#series_index", Input).value
            self.app.custom_stylesheet = self.query_one("#stylesheet_input", TextArea).text
            self.app.pop_screen()
        elif event.button.id == "back_to_main":
            self.app.pop_screen()


class WebToEpubApp(App):
    """A Textual app to convert web novels to EPUB."""

    CSS_PATH = "tui.css"

    def __init__(self):
        super().__init__()
        # Default settings
        self.custom_stylesheet = None
        self.skip_images = False
        self.epub3 = False
        self.series_name = None
        self.series_index = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container():
            yield Input(placeholder="Enter novel URL here...", id="url_input")
            with Horizontal(classes="button-bar"):
                yield Button("Download", variant="primary", id="download_button")
                yield Button("Settings", id="settings_button")
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
        elif event.button.id == "settings_button":
            self.push_screen(SettingsScreen())

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
        epub_generator = EpubGenerator(
            title,
            author,
            custom_stylesheet=self.custom_stylesheet,
            epub3=self.epub3,
            series_name=self.series_name,
            series_index=self.series_index
        )

        if not self.skip_images:
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
