from ebooklib import epub

class EpubWriter:
    def __init__(self, title, author, language="en"):
        self.book = epub.EpubBook()
        self.book.set_identifier("id123456")  # A unique identifier is required
        self.book.set_title(title)
        self.book.set_language(language)
        self.book.add_author(author)

    def add_chapter(self, title, content, chapter_number):
        file_name = f"chapter_{chapter_number}.xhtml"
        chapter = epub.EpubHtml(title=title, file_name=file_name, lang="en")
        chapter.content = content
        self.book.add_item(chapter)
        return chapter

    def write_epub(self, chapters, output_filename):
        """
        Generates the EPUB file.

        :param chapters: A list of dictionaries, where each dictionary has 'title' and 'content' keys.
        :param output_filename: The name of the file to save the EPUB to.
        """

        # Add chapters to the book
        book_chapters = []
        for i, chap_data in enumerate(chapters):
            chapter = self.add_chapter(chap_data['title'], chap_data['content'], i + 1)
            book_chapters.append(chapter)

        # Define the book's table of contents
        self.book.toc = (epub.Link('intro', 'Introduction', 'intro.xhtml'),
                         (epub.Section('Chapters'),
                          tuple(book_chapters))
                        )

        # Add default NCX and Nav files
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # Define the book's spine
        self.book.spine = ['nav'] + book_chapters

        # Write the EPUB file
        epub.write_epub(output_filename, self.book, {})
