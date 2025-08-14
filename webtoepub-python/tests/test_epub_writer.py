import pytest
from pathlib import Path
from webtoepub.epub_writer import EpubWriter

@pytest.fixture
def epub_writer():
    """Fixture to create an EpubWriter instance for testing."""
    return EpubWriter(title="Test Book", author="Test Author")

def test_create_epub(epub_writer, tmp_path):
    """
    Test that an EPUB file can be created successfully.
    """
    output_dir = tmp_path
    output_filename = output_dir / "test_book.epub"

    chapters = [
        {"title": "Chapter 1", "content": "<h1>Chapter 1</h1><p>This is the first chapter.</p>"},
        {"title": "Chapter 2", "content": "<h1>Chapter 2</h1><p>This is the second chapter.</p>"},
    ]

    # The EpubWriter in its current form doesn't take the output filename in the constructor or write_epub
    # I need to adapt the test to the current implementation.
    # The current implementation writes the file in the write_epub method.

    writer = EpubWriter(title="Test Book", author="Test Author")
    writer.write_epub(chapters, str(output_filename))

    assert output_filename.exists()
    assert output_filename.is_file()

    # Optional: read the epub and verify its contents
    # For now, just checking for existence is enough to validate the basic functionality.
