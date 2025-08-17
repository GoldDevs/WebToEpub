"""
This module contains the ParserFactory for creating parser instances.
"""
from urllib.parse import urlparse
from .parsers.novel_full_parser import NovelFullParser, Novel35Parser, NovelHyphenBinParser, NovelbinParser
from .parsers.default_parser import DefaultParser

# A dictionary mapping hostnames to parser classes
PARSER_MAP = {
    'allnovel.org': NovelFullParser,
    'allnovelbin.net': NovelFullParser,
    'allnovelfull.app': NovelFullParser,
    'allnovelfull.com': NovelFullParser,
    'allnovelfull.org': NovelFullParser,
    'allnovelfull.net': NovelFullParser,
    'allnovelnext.com': NovelFullParser,
    'all-novelfull.net': NovelFullParser,
    'boxnovelfull.com': NovelFullParser,
    'freenovelsread.com': NovelFullParser,
    'freewn.com': NovelFullParser,
    'novel-next.com': NovelFullParser,
    'novelactive.org': NovelFullParser,
    'novelbin.me': NovelFullParser,
    'novelbin.net': NovelFullParser,
    'novelbin.org': NovelFullParser,
    'novelebook.net': NovelFullParser,
    'novelfull.com': NovelFullParser,
    'novelfull.net': NovelFullParser,
    'novelfullbook.com': NovelFullParser,
    'novelfulll.com': NovelFullParser,
    'novelhulk.net': NovelFullParser,
    'novelmax.net': NovelFullParser,
    'novelnext.com': NovelFullParser,
    'novelnext.dramanovels.io': NovelFullParser,
    'novelnext.net': NovelFullParser,
    'novelnextz.com': NovelFullParser,
    'noveltop1.org': NovelFullParser,
    'noveltrust.net': NovelFullParser,
    'novelusb.com': NovelFullParser,
    'novelusb.net': NovelFullParser,
    'novelxo.net': NovelFullParser,
    'readnovelfull.me': NovelFullParser,
    'thenovelbin.org': NovelFullParser,
    'topnovelfull.com': NovelFullParser,
    'zinnovel.net': NovelFullParser,
    # Parsers for variations
    'novel35.com': Novel35Parser,
    'novel-bin.com': NovelHyphenBinParser,
    'novel-bin.net': NovelHyphenBinParser,
    'novel-bin.org': NovelHyphenBinParser,
    'novelbin.com': NovelbinParser,
}

def get_parser(url, force_default=False):
    """
    Returns the appropriate parser for the given URL.
    If force_default is True, it will always return the DefaultParser.
    """
    if force_default:
        return DefaultParser

    hostname = urlparse(url).hostname
    if hostname:
        # handle www. prefix
        if hostname.startswith('www.'):
            hostname = hostname[4:]
        parser = PARSER_MAP.get(hostname)
        if parser:
            return parser

    # If no specific parser is found, return the DefaultParser
    return DefaultParser
