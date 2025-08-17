# Web to EPUB (Python)

## Attribution

This project is a full conversion and rewrite of the original [WebToEpub](https://github.com/dteviot/WebToEpub) browser extension by `dteviot` into a modern, standalone Python application. All credit for the original concept, parser logic, and immense website support goes to the original author and the many contributors to that project.

This Python version was created to provide a command-line and TUI-based tool that is compatible with a wide range of systems, including Termux on Android.

---

This is a Python command-line tool to convert web novels from various sources into EPUB format.

## Features

-   Convert web novels to EPUB format.
-   Supports multiple web novel sites (currently focused on 'novel*' sites).
-   Command-line interface for easy use in scripts and automated workflows.
-   Extensible architecture to easily add new parsers for other websites.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd web-to-epub
    ```

2.  **Install the package:**
    ```bash
    pip install .
    ```
    This will install the necessary dependencies and make the `web-to-epub` command available in your shell.

## Usage

This tool uses a Text-based User Interface (TUI). To start it, simply run the `web-to-epub` command in your terminal:

```bash
web-to-epub
```

This will launch the application. From there, you can:

1.  Enter the URL of the novel you want to convert into the input box.
2.  Press the "Download" button.
3.  Watch the progress in the log window.
4.  The generated EPUB file will be saved in the directory where you ran the command.

The TUI is designed with a "mobile first" approach, ensuring it is usable on small screens, such as a phone running Termux.

### Advanced Settings

The TUI includes a "Settings" button which opens a new screen with advanced options:

-   **Skip Images:** A checkbox to prevent any images from being downloaded.
-   **Create EPUB 3:** A checkbox to create an EPUB 3 compliant file (defaults to EPUB 2).
-   **Series & Volume:** Input fields to add Calibre-compatible series metadata to the EPUB.
-   **Custom Stylesheet:** A text area to provide your own CSS for styling the EPUB content.

## Supported Sites

This tool currently supports a subset of the sites supported by the original WebToEpub extension, with a focus on sites with "novel" in their names. The supported sites include:

-   novelfull.com
-   novelbin.com
-   and many others handled by the `NovelFullParser`.

You can find the full list of supported domains in the `src/web_to_epub/parser_factory.py` file.

## Extending with New Parsers

The tool is designed to be easily extensible with new parsers for other websites. To add a new parser, you need to:

1.  Create a new parser class that inherits from `web_to_epub.parser.Parser`. This class should be placed in the `src/web_to_epub/parsers/` directory.
2.  Implement the required methods in your parser class:
    -   `get_title()`: Returns the title of the novel.
    -   `get_author()`: Returns the author of the novel.
    -   `get_cover_image_url()`: Returns the URL of the cover image.
    -   `get_chapter_urls()`: Returns a list of URLs for all the chapters.
    -   `get_chapter_content()`: Extracts the content of a single chapter.
    -   `get_chapter_title()`: Extracts the title of a single chapter.
3.  Add your new parser to the `PARSER_MAP` in `src/web_to_epub/parser_factory.py`, mapping the website's hostname to your new parser class.

## Compatibility

This tool is a pure Python package and should be compatible with any system that has Python 3.7+ installed, including:

-   Windows
-   macOS
-   Linux
-   Termux (on Android)
