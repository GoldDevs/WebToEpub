import io
import concurrent.futures
import threading
from PIL import Image
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Input, Static, RichLog, TextArea, Checkbox
from textual.worker import work
from textual.screen import Screen, ModalScreen

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
            yield Checkbox("Use full title as filename", id="full_title_filename", value=self.app.use_full_title_filename)
            yield Checkbox("Include TOC page as chapter", id="toc_as_chapter", value=self.app.toc_as_chapter)
            yield Checkbox("Add information page", id="add_info_page", value=self.app.add_info_page)
            yield Checkbox("Remove next/prev chapter links", id="remove_nav_links", value=self.app.remove_nav_links)
            yield Checkbox("Skip chapters that fail to download", id="skip_failed_chapters", value=self.app.skip_failed_chapters)
            yield Checkbox("Compress images", id="compress_images", value=self.app.compress_images)
            yield Static("Max image resolution:", classes="label")
            yield Input(id="max_image_res", value=str(self.app.max_image_res), type="integer")
            yield Static("Max chapters per EPUB (0 for unlimited):", classes="label")
            yield Input(id="max_chapters_per_epub", value=str(self.app.max_chapters_per_epub), type="integer")
            yield Static("Max concurrent downloads:", classes="label")
            yield Input(id="max_concurrent_downloads", value=str(self.app.max_concurrent_downloads), type="integer")
            yield Static("Number of retries on error:", classes="label")
            yield Input(id="num_retries", value=str(self.app.num_retries), type="integer")
            yield Static("Series:", classes="label")
            yield Input(id="series_name", value=self.app.series_name or "")
            yield Static("Volume:", classes="label")
            yield Input(id="series_index", value=self.app.series_index or "")
            yield Static("Subject (Tags, comma-separated):", classes="label")
            yield Input(id="subject", value=self.app.subject or "")
            yield Static("Description:", classes="label")
            yield TextArea(self.app.description or "", id="description")
            yield Static("Translator:", classes="label")
            yield Input(id="translator", value=self.app.translator or "")
            yield Static("Author File As:", classes="label")
            yield Input(id="file_as", value=self.app.file_as or "")
            yield Static("Manual download delay (ms):", classes="label")
            yield Input(id="download_delay", value=str(self.app.download_delay), type="integer")
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
            self.app.use_full_title_filename = self.query_one("#full_title_filename", Checkbox).value
            self.app.toc_as_chapter = self.query_one("#toc_as_chapter", Checkbox).value
            self.app.add_info_page = self.query_one("#add_info_page", Checkbox).value
            self.app.remove_nav_links = self.query_one("#remove_nav_links", Checkbox).value
            self.app.skip_failed_chapters = self.query_one("#skip_failed_chapters", Checkbox).value
            self.app.compress_images = self.query_one("#compress_images", Checkbox).value
            self.app.max_image_res = int(self.query_one("#max_image_res", Input).value or 1080)
            self.app.max_chapters_per_epub = int(self.query_one("#max_chapters_per_epub", Input).value or 0)
            self.app.max_concurrent_downloads = int(self.query_one("#max_concurrent_downloads", Input).value or 1)
            self.app.num_retries = int(self.query_one("#num_retries", Input).value or 3)
            self.app.series_name = self.query_one("#series_name", Input).value
            self.app.series_index = self.query_one("#series_index", Input).value
            self.app.subject = self.query_one("#subject", Input).value
            self.app.description = self.query_one("#description", TextArea).text
            self.app.translator = self.query_one("#translator", Input).value
            self.app.file_as = self.query_one("#file_as", Input).value
            self.app.download_delay = int(self.query_one("#download_delay", Input).value or 0)
            self.app.custom_stylesheet = self.query_one("#stylesheet_input", TextArea).text
            self.app.pop_screen()
        elif event.button.id == "back_to_main":
            self.app.pop_screen()

class ErrorScreen(ModalScreen):
    """A modal screen to display an error and get user action."""
    def __init__(self, error_message: str) -> None:
        super().__init__()
        self.error_message = error_message

    def compose(self) -> ComposeResult:
        with Container(id="error_dialog"):
            yield Static(self.error_message, id="error_message")
            with Horizontal(classes="button-bar"):
                yield Button("Retry", variant="primary", id="retry")
                yield Button("Skip", id="skip")
                yield Button("Abort", variant="error", id="abort")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id)

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
        self.subject = None
        self.description = None
        self.translator = None
        self.file_as = None
        self.use_full_title_filename = False
        self.toc_as_chapter = False
        self.download_delay = 0
        self.add_info_page = True
        self.remove_nav_links = True
        self.skip_failed_chapters = False
        self.compress_images = False
        self.max_image_res = 1080
        self.max_chapters_per_epub = 0 # 0 means unlimited
        self.max_concurrent_downloads = 4
        self.num_retries = 3

        # For interactive error handling
        self.error_event = threading.Event()
        self.error_choice = None

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
        downloader = Downloader(delay=self.download_delay)
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

        # Handle filename generation
        if self.use_full_title_filename:
            import re
            safe_title = re.sub(r'[\\/*?:"<>|]',"", title)
            output_filename = f"{safe_title}.epub"
        else:
            output_filename = f"{title.split(' ')[0]}.epub"

        log.write(f"Creating '{output_filename}' by {author}")
        epub_generator = EpubGenerator(
            title,
            author,
            custom_stylesheet=self.custom_stylesheet,
            epub3=self.epub3,
            series_name=self.series_name,
            series_index=self.series_index,
            subject=self.subject,
            description=self.description,
            translator=self.translator,
            file_as=self.file_as
        )

        if not self.skip_images:
            cover_url = parser_instance.get_cover_image_url()
            if cover_url:
                log.write("Downloading cover image...")
                try:
                    cover_content = downloader.session.get(cover_url, timeout=10).content
                    if self.compress_images:
                        log.write("Compressing cover image...")
                        cover_content = self._compress_image(cover_content)
                    cover_filename = cover_url.split('/')[-1]
                    epub_generator.set_cover(cover_content, cover_filename)
                except Exception as e:
                    log.write(f"Could not download cover image: {e}")

        # Handle including TOC as chapter
        if self.toc_as_chapter:
            toc_content = parser_instance.get_chapter_content(index_page_content)
            epub_generator.add_chapter("Table of Contents", toc_content, 0)

        # Add information page if requested
        if self.add_info_page:
            epub_generator.add_information_page()

        chapter_urls = parser_instance.get_chapter_urls(downloader)
        log.write(f"Found {len(chapter_urls)} chapters.")

        for i, chapter_url in enumerate(chapter_urls):
            try:
                log.write(f"Downloading chapter {i+1}/{len(chapter_urls)}...")
                self.call_from_thread(log.refresh) # Refresh the log
                chapter_content_html = downloader.get(chapter_url)
                if chapter_content_html:
                    chapter_title = parser_instance.get_chapter_title(chapter_content_html) or f"Chapter {i+1}"
                    chapter_content = parser_instance.get_chapter_content(
                        chapter_content_html,
                        chapter_urls=chapter_urls,
                        remove_nav_links=self.remove_nav_links
                    )
                    epub_generator.add_chapter(chapter_title, chapter_content, i+1)
                else:
                    if not self.skip_failed_chapters:
                        log.write(f"Failed to download chapter {i+1}. Halting.")
                        return
                    else:
                        log.write(f"Failed to download chapter {i+1}. Skipping.")
            except Exception as e:
                if not self.skip_failed_chapters:
                    log.write(f"An error occurred on chapter {i+1}: {e}. Halting.")
                    return
                else:
                    log.write(f"An error occurred on chapter {i+1}: {e}. Skipping.")

        # Parallel chapter download
        chapters_to_download = list(enumerate(chapter_urls))
        chapters_data = [None] * len(chapters_to_download)

        while chapters_to_download:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_downloads) as executor:
                future_to_chapter = {executor.submit(self._download_chapter, i, url, downloader, parser_instance, chapter_urls): (i, url) for i, url in chapters_to_download}
                chapters_to_download = [] # Clear the list for retries

                for future in concurrent.futures.as_completed(future_to_chapter):
                    i, url = future_to_chapter[future]
                    try:
                        data = future.result()
                        if data:
                            chapters_data[i] = data
                            log.write(f"Successfully downloaded chapter {i+1}")
                        else:
                            log.write(f"Failed to download chapter {i+1} after all retries.")
                    except Exception as exc:
                        if self.skip_failed_chapters:
                            log.write(f"Chapter {i+1} failed: {exc}. Skipping.")
                            continue

                        self.error_event.clear()
                        self.call_from_thread(self.push_screen, ErrorScreen(f"Error on chapter {i+1}: {exc}"), self.handle_error_choice)
                        self.error_event.wait() # Pause worker until user makes a choice

                        if self.error_choice == 'retry':
                            log.write(f"Retrying chapter {i+1}...")
                            chapters_to_download.append((i, url)) # Add back to the list for retry
                        elif self.error_choice == 'abort':
                            log.write("Download aborted by user.")
                            self.query_one("#download_button").disabled = False
                            return
                        elif self.error_choice == 'skip':
                            log.write(f"Skipping chapter {i+1}.")
                            continue

        # Now add chapters to epub in correct order, handling volume splitting
        volume_number = 1
        chapters_in_volume = 0
        for i, data in enumerate(chapters_data):
            if data is None:
                continue

            # Check if we need to start a new volume
            if self.max_chapters_per_epub > 0 and chapters_in_volume >= self.max_chapters_per_epub:
                vol_filename = output_filename.replace('.epub', f'-v{volume_number}.epub')
                epub_generator.save(vol_filename)
                log.write(f"Saved volume {volume_number} as {vol_filename}")

                volume_number += 1
                chapters_in_volume = 0
                epub_generator = EpubGenerator(
                    title, author,
                    custom_stylesheet=self.custom_stylesheet, epub3=self.epub3,
                    series_name=self.series_name, series_index=f"{self.series_index or ''}-{volume_number}",
                    subject=self.subject, description=self.description,
                    translator=self.translator, file_as=self.file_as
                )

            chapter_title, chapter_content = data
            epub_generator.add_chapter(chapter_title, chapter_content, i + 1)
            chapters_in_volume += 1

        # Save the final/only volume
        final_filename = output_filename
        if volume_number > 1:
            final_filename = output_filename.replace('.epub', f'-v{volume_number}.epub')
        epub_generator.save(final_filename)
        log.write(f"Epub saved as {final_filename}")
        self.query_one("#download_button").disabled = False

    def handle_error_choice(self, choice: str) -> None:
        """Callback to handle the user's choice from the error screen."""
        self.error_choice = choice
        self.error_event.set()

    def _download_chapter(self, chapter_index, chapter_url, downloader, parser, all_chapter_urls):
        """Helper method to download and parse a single chapter."""
        try:
            chapter_content_html = downloader.get(chapter_url, num_retries=self.num_retries)
            if chapter_content_html:
                chapter_title = parser.get_chapter_title(chapter_content_html) or f"Chapter {chapter_index + 1}"
                chapter_content = parser.get_chapter_content(
                    chapter_content_html,
                    chapter_urls=all_chapter_urls,
                    remove_nav_links=self.remove_nav_links
                )
                return chapter_title, chapter_content
        except Exception as e:
            # Re-raise the exception to be caught by the main loop
            raise e
        return None

    def _compress_image(self, image_content: bytes) -> bytes:
        """Compresses an image if it's larger than the max resolution."""
        try:
            with Image.open(io.BytesIO(image_content)) as img:
                if max(img.size) > self.max_image_res:
                    img.thumbnail((self.max_image_res, self.max_image_res))

                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                return buffer.getvalue()
        except Exception as e:
            log = self.query_one("#logs", RichLog)
            log.write(f"Could not compress image: {e}")
            return image_content # Return original content on failure


def main():
    """Run the Textual app."""
    app = WebToEpubApp()
    app.run()

if __name__ == "__main__":
    main()
