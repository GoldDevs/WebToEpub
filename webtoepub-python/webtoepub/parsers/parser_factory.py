from urllib.parse import urlparse
from .base_parser import Parser

class ParserFactory:
    _parsers = {}

    @classmethod
    def register(cls, domain: str, parser_class):
        if not issubclass(parser_class, Parser):
            raise TypeError(f"{parser_class.__name__} is not a subclass of Parser")
        cls._parsers[domain] = parser_class

    @classmethod
    def get_parser(cls, url: str) -> Parser:
        """
        Returns an instance of the appropriate parser for the given URL.
        """
        domain = urlparse(url).netloc
        # Remove "www." if it exists
        if domain.startswith("www."):
            domain = domain[4:]

        parser_class = cls._parsers.get(domain)
        if not parser_class:
            raise ValueError(f"No parser found for domain: {domain}")
        return parser_class()
