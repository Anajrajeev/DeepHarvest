"""
Soft 404 Detection
"""
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class Soft404Detector:
    """Detect soft 404 pages (pages that return 200 but are actually errors)"""
    
    SOFT_404_INDICATORS = [
        'not found',
        '404',
        'page not found',
        'does not exist',
        'no longer available',
        'error',
        'oops'
    ]
    
    async def load(self):
        """Load model"""
        logger.info("Soft 404 detector loaded")
    
    async def is_soft_404(self, response) -> bool:
        """Detect if page is a soft 404"""
        
        if not response:
            return False
        
        # Check status code
        status_code = getattr(response, 'status_code', None)
        if status_code in [404, 410]:
            return True
        
        # Check content
        if not hasattr(response, 'text') or not response.text:
            return False
        
        text = response.text.lower()
        
        # Count indicators
        indicator_count = sum(1 for indicator in self.SOFT_404_INDICATORS if indicator in text)
        
        # Check content length (very short pages often are errors)
        if len(text) < 500 and indicator_count > 0:
            return True
        
        if indicator_count >= 3:
            return True
        
        # Check title
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('title')
        
        if title and any(indicator in title.get_text().lower() for indicator in self.SOFT_404_INDICATORS):
            return True
        
        return False

