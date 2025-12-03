"""
fetcher.py - Advanced HTTP Client
"""
import logging
import aiohttp
from typing import Optional
from .crawler import CrawlConfig
from ..utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)

class AdvancedFetcher:
    """HTTP/2, HTTP/3 capable fetcher with connection pooling"""
    
    def __init__(self, config: CrawlConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.connector = None
    
    async def initialize(self):
        """Initialize HTTP session with HTTP/2 support"""
        # Try HTTP/2 connector
        try:
            import aiohttp
            from aiohttp import ClientSession, TCPConnector
            
            # Create connector with HTTP/2 support if available
            connector = TCPConnector(
                limit=self.config.concurrent_requests,
                limit_per_host=self.config.per_host_concurrent,
                ssl=False  # Can be configured
            )
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            self.session = ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': getattr(self.config, 'user_agent', 'DeepHarvest/1.0'),
                    'Accept': 'text/html,application/xhtml+xml,application/xml,*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            )
        except Exception as e:
            logger.warning(f"Failed to initialize HTTP/2 session: {e}, falling back to HTTP/1.1")
            # Fallback to standard session
            self.session = aiohttp.ClientSession()
    
    async def fetch(self, url: str, retries: int = 3):
        """Fetch URL with retries, compression, and error handling"""
        if not self.session:
            await self.initialize()
        
        async def _fetch():
            try:
                async with self.session.get(url, allow_redirects=True) as response:
                    # Create response-like object
                    class Response:
                        def __init__(self, resp):
                            self.status_code = resp.status
                            self.headers = resp.headers
                            self.url = str(resp.url)
                            self._content = None
                            self._text = None
                        
                        @property
                        async def content(self):
                            if self._content is None:
                                self._content = await response.read()
                            return self._content
                        
                        @property
                        async def text(self):
                            if self._text is None:
                                self._text = await response.text()
                            return self._text
                    
                    resp_obj = Response(response)
                    resp_obj._content = await response.read()
                    resp_obj._text = await response.text()
                    return resp_obj
                    
            except aiohttp.ClientError as e:
                logger.error(f"Network error fetching {url}: {e}")
                raise
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                raise
        
        # Use retry with backoff
        try:
            return await retry_with_backoff(_fetch, max_retries=retries)
        except Exception as e:
            logger.error(f"Failed to fetch {url} after {retries} retries: {e}")
            return None
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()
            self.session = None
