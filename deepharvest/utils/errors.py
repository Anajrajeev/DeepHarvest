"""
Error classification
"""
import logging

logger = logging.getLogger(__name__)

class CrawlError(Exception):
    """Base crawl error"""
    pass

class NetworkError(CrawlError):
    """Network-related error"""
    pass

class ParseError(CrawlError):
    """Parsing error"""
    pass

class TrapDetectedError(CrawlError):
    """Trap detected error"""
    pass

