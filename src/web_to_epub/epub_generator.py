"""
This module contains the EpubGenerator class for creating EPUB files.
"""
import uuid
from ebooklib import epub

class EpubGenerator:
    def __init__(self, title, author, language='en'):
        self.book = epub.EpubBook()
        self.book.set_title(title)
        self.book.set_author(author)
        self.book.set_language(language)
        self.book.set_identifier(str(uuid.uuid4()))
        self.chapters = []

    def add_chapter(self, title, content, chapter_number):
        """
        Adds a chapter to the EPUB book.
        """
        file_name = f'chapter_{chapter_number}.xhtml'
        chapter = epub.EpubHtml(title=title, file_name=file_name, lang=self.book.language)
        chapter.content = content
        self.book.add_item(chapter)
        self.chapters.append(chapter)

    def set_cover(self, image_content, image_filename):
        """
        Sets the cover image for the EPUB book.
        """
        self.book.set_cover(image_filename, image_content)

    def save(self, filename):
        """
        Saves the EPUB book to a file.
        """
        self.book.toc = self.chapters
        self.book.spine = ['cover', 'nav'] + self.chapters
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        epub.write_epub(filename, self.book, {})
