from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class Parser(ABC):
    """
    Abstract base class for a website parser.
    """

    @abstractmethod
    def get_title(self, url: str, soup: BeautifulSoup) -> str:
        """
        Extracts the title of the web novel.
        """
        pass

    @abstractmethod
    def get_author(self, url: str, soup: BeautifulSoup) -> str:
        """
        Extracts the author of the web novel.
        """
        pass

    @abstractmethod
    def get_chapter_urls(self, url: str, soup: BeautifulSoup) -> list[str]:
        """
        Extracts the URLs of all chapters.
        """
        pass

    @abstractmethod
    def get_chapter_title(self, soup: BeautifulSoup) -> str:
        """
        Extracts the title of a single chapter from its soup.
        """
        pass

    @abstractmethod
    def extract_content(self, url: str, soup: BeautifulSoup) -> str:
        """
        Extracts the main content of a chapter.
        """
        pass
