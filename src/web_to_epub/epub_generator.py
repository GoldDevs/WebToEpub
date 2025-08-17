"""
This module contains the EpubGenerator class for creating EPUB files.
"""
import uuid
from ebooklib import epub

class EpubGenerator:
    DEFAULT_CSS = """
    body {
        font-family: sans-serif;
    }
    p {
        text-indent: 1em;
        margin-top: 0;
        margin-bottom: 0;
    }
    """

    def __init__(self, title, author, language='en', custom_stylesheet=None, epub3=False,
                 series_name=None, series_index=None, subject=None, description=None,
                 translator=None, file_as=None):
        self.book = epub.EpubBook()
        self.book.set_title(title)
        self.book.add_author(author, file_as=file_as)
        self.book.set_language(language)
        self.book.set_identifier(str(uuid.uuid4()))
        if epub3:
            self.book.version = '3.0'
        if series_name and series_index:
            self.book.add_metadata('calibre', 'series', series_name)
            self.book.add_metadata('calibre', 'series_index', series_index)
        if subject:
            for tag in subject.split(','):
                self.book.add_metadata('DC', 'subject', tag.strip())
        if description:
            self.book.add_metadata('DC', 'description', description)
        if translator:
            self.book.add_author(translator, role='trl')

        self.chapters = []
        self.stylesheet = custom_stylesheet if custom_stylesheet is not None else self.DEFAULT_CSS

    def add_chapter(self, title, content, chapter_number):
        """
        Adds a chapter to the EPUB book.
        """
        file_name = f'chapter_{chapter_number}.xhtml'
        chapter = epub.EpubHtml(title=title, file_name=file_name, lang=self.book.language)
        chapter.content = content
        # Add stylesheet link
        chapter.add_link(href='style/main.css', rel='stylesheet', type='text/css')
        self.book.add_item(chapter)
        self.chapters.append(chapter)

    def set_cover(self, image_content, image_filename):
        """
        Sets the cover image for the EPUB book.
        """
        self.book.set_cover(image_filename, image_content)

    def add_information_page(self):
        """
        Adds an information page to the EPUB book with all the metadata.
        """
        content = f"<h1>About this book</h1>"
        content += f"<h2>Title: {self.book.title}</h2>"
        for author in self.book.get_metadata('DC', 'creator'):
            content += f"<p><b>Author:</b> {author[0]}</p>"
        for subject in self.book.get_metadata('DC', 'subject'):
            content += f"<p><b>Tags:</b> {subject[0]}</p>"
        description = self.book.get_metadata('DC', 'description')
        if description:
            content += f"<h3>Description</h3><p>{description[0][0]}</p>"

        info_chapter = epub.EpubHtml(title="Information", file_name="info.xhtml", lang=self.book.language)
        info_chapter.content = content
        info_chapter.add_link(href='style/main.css', rel='stylesheet', type='text/css')

        self.book.add_item(info_chapter)
        # Add to beginning of chapters list and spine
        self.chapters.insert(0, info_chapter)


    def save(self, filename):
        """
        Saves the EPUB book to a file.
        """
        # Add stylesheet
        style = epub.EpubItem(uid="style_main", file_name="style/main.css", media_type="text/css", content=self.stylesheet)
        self.book.add_item(style)

        self.book.toc = self.chapters
        self.book.spine = ['cover', 'nav'] + self.chapters
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        epub.write_epub(filename, self.book, {})
