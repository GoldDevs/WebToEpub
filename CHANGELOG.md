# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-08-17

### Added
- **Initial Python Conversion:**
  - Converted the entire project from a JavaScript browser extension to a standalone Python 3 package.
  - Created a modern Python project structure with `pyproject.toml`.
  - Implemented core components: `Downloader`, `EpubGenerator`, and a base `Parser` class.
- **Text-based User Interface (TUI):**
  - Created a user-friendly TUI using the Textual library, replacing the original browser popup UI.
  - The TUI is designed to be mobile-friendly for use with Termux.
- **Parser Implementation:**
  - Ported the complex `NovelFullParser` and its variants (`Novel35Parser`, `NovelHyphenBinParser`, `NovelbinParser`).
  - Added a `DefaultParser` as a fallback for unsupported websites.
  - Ported the API-based `WtrLabParser`.
- **Advanced Settings:**
  - Implemented a comprehensive Settings screen in the TUI.
  - **Metadata:** Added options for Subject (tags), Description, Translator, Series, and Volume.
  - **Content & File Handling:** Added options for custom stylesheets, adding an information page, including the TOC page as a chapter, and using the full title for the filename.
  - **Image Handling:** Added options to skip or compress images, with a configurable max resolution (requires Pillow).
  - **EPUB Splitting:** Added an option to split large EPUBs into multiple volumes based on a max chapter count.
- **Robust Downloader:**
  - **Parallel Downloads:** Re-architected the downloader to use a thread pool for concurrent chapter downloads.
  - **Rate-Limiting:** The downloader now automatically handles HTTP 429 "Too Many Requests" errors and `Retry-After` headers.
  - **Retries:** Implemented an automatic retry mechanism with exponential backoff for failed downloads.
  - **Interactive Error Handling:** If a chapter download fails permanently, the TUI now presents the user with "Retry", "Skip", and "Abort" options.
- **Documentation & Testing:**
  - Created a comprehensive `README.md` with installation and usage instructions.
  - Added unit tests for all implemented parsers and the `EpubGenerator`.
- **Licensing:**
  - Changed the project license from GPLv3 to MIT License for the new Python version.

### Changed
- The project is now a command-line application installable via `pip`, instead of a browser extension.
