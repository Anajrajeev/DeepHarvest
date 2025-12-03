"""
Core Crawler Orchestrator
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List, Set
from enum import Enum
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
import aiohttp
from playwright.async_api import async_playwright
from datetime import datetime

logger = logging.getLogger(__name__)

class CrawlStrategy(Enum):
    BFS = "breadth_first"
    DFS = "depth_first"
    PRIORITY = "priority"

@dataclass
class CrawlConfig:
    """Comprehensive crawl configuration"""
    seed_urls: List[str]
    strategy: CrawlStrategy = CrawlStrategy.BFS
    max_depth: Optional[int] = None  # None = infinite
    follow_subdomains: bool = True
    follow_external: bool = False
    
    # Content types to crawl
    extract_text: bool = True
    extract_pdfs: bool = True
    extract_office: bool = True
    extract_images: bool = True
    extract_videos: bool = True
    extract_audio: bool = True
    
    # JavaScript rendering
    enable_js: bool = True
    wait_for_js_ms: int = 2000
    handle_infinite_scroll: bool = True
    
    # Storage
    output_dir: str = "./crawl_output"
    streaming_threshold_mb: int = 50
    
    # Distributed mode
    distributed: bool = False
    redis_url: Optional[str] = None
    worker_id: Optional[str] = None
    
    # Rate limiting
    concurrent_requests: int = 10
    per_host_concurrent: int = 2
    request_delay_ms: int = 100
    
    # Resumability
    checkpoint_interval: int = 100
    state_file: str = "crawl_state.json"
    
    # ML features
    enable_ml_extraction: bool = True
    enable_trap_detection: bool = True
    enable_soft404_detection: bool = True
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

class DeepHarvest:
    """
    Main crawler orchestrator coordinating all subsystems
    """
    
    def __init__(self, config: CrawlConfig):
        self.config = config
        self.frontier = None
        self.fetcher = None
        self.js_engine = None
        self.extractors = {}
        self.ml_models = {}
        self.visited: Set[str] = set()
        self.stats = CrawlStats()
        
    async def initialize(self):
        """Initialize all subsystems"""
        logger.info("Initializing DeepHarvest...")
        
        # Initialize frontier
        if self.config.distributed:
            from ..distributed.redis_frontier import RedisFrontier
            self.frontier = RedisFrontier(self.config.redis_url)
            await self.frontier.connect()
        else:
            from .frontier import LocalFrontier
            self.frontier = LocalFrontier(self.config.strategy)
        
        # Initialize fetcher
        from .fetcher import AdvancedFetcher
        self.fetcher = AdvancedFetcher(self.config)
        await self.fetcher.initialize()
        
        # Initialize JS engine if enabled
        if self.config.enable_js:
            from ..engines.js_renderer import JSRenderer
            self.js_engine = JSRenderer(self.config)
            await self.js_engine.initialize()
        
        # Initialize extractors
        await self._initialize_extractors()
        
        # Initialize ML models if enabled
        if self.config.enable_ml_extraction:
            await self._initialize_ml_models()
        
        # Load checkpoint if resuming
        await self._load_checkpoint()
        
        logger.info("DeepHarvest initialized successfully")
    
    async def _initialize_extractors(self):
        """Initialize all content extractors"""
        from ..extractors.text import TextExtractor
        from ..extractors.pdf import PDFExtractor
        from ..extractors.office import OfficeExtractor
        from ..extractors.media import MediaExtractor
        from ..extractors.ocr import OCRExtractor
        from ..extractors.structured import StructuredDataExtractor
        
        self.extractors['text'] = TextExtractor()
        self.extractors['pdf'] = PDFExtractor()
        self.extractors['office'] = OfficeExtractor()
        self.extractors['media'] = MediaExtractor()
        self.extractors['ocr'] = OCRExtractor()
        self.extractors['structured'] = StructuredDataExtractor()
    
    async def _initialize_ml_models(self):
        """Initialize ML models for intelligent extraction"""
        from ..ml.classifier import PageClassifier
        from ..ml.soft404 import Soft404Detector
        from ..ml.quality import QualityScorer
        from ..ml.dedup import NearDuplicateDetector
        
        self.ml_models['classifier'] = PageClassifier()
        self.ml_models['soft404'] = Soft404Detector()
        self.ml_models['quality'] = QualityScorer()
        self.ml_models['dedup'] = NearDuplicateDetector()
        
        # Load pre-trained models
        for model in self.ml_models.values():
            await model.load()
    
    async def crawl(self):
        """Main crawl loop"""
        logger.info(f"Starting crawl with {len(self.config.seed_urls)} seed URLs")
        
        # Add seed URLs to frontier
        for url in self.config.seed_urls:
            await self.frontier.add(url, depth=0, priority=1.0)
        
        # Create worker tasks
        workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self.config.concurrent_requests)
        ]
        
        # Wait for all workers to complete
        await asyncio.gather(*workers)
        
        logger.info("Crawl completed")
        await self._generate_reports()
    
    async def _worker(self, worker_id: int):
        """Worker coroutine for processing URLs"""
        while True:
            # Get next URL from frontier
            item = await self.frontier.get()
            if item is None:
                break
            
            url, depth, priority = item
            
            try:
                await self._process_url(url, depth)
            except Exception as e:
                logger.error(f"Error processing {url}: {e}", exc_info=True)
                self.stats.errors += 1
            finally:
                await self.frontier.mark_done(url)
                self.stats.processed += 1
                
                # Checkpoint periodically
                if self.stats.processed % self.config.checkpoint_interval == 0:
                    await self._save_checkpoint()
    
    async def _process_url(self, url: str, depth: int):
        """Process a single URL"""
        logger.debug(f"Processing {url} at depth {depth}")
        
        # Check if already visited (distributed-safe)
        if await self._is_visited(url):
            return
        
        # Fetch content
        response = await self.fetcher.fetch(url)
        if response is None:
            return
        
        # Mark as visited
        await self._mark_visited(url)
        
        # Render JavaScript if needed (auto-detect blank HTML)
        if self.config.enable_js:
            needs_js = self._needs_js_rendering(response)
            # Also check if HTML is mostly empty (likely needs JS)
            if not needs_js and hasattr(response, 'text'):
                text_len = len(response.text.strip())
                if text_len < 500:  # Very short HTML, likely needs JS
                    needs_js = True
            
            if needs_js:
                response = await self.js_engine.render(url, response)
        
        # Detect traps
        if self.config.enable_trap_detection:
            if await self._is_trap(url, response):
                logger.warning(f"Trap detected: {url}")
                return
        
        # Detect soft 404
        if self.config.enable_soft404_detection:
            if await self._is_soft_404(response):
                logger.info(f"Soft 404 detected: {url}")
                return
        
        # Extract content based on content type
        content = await self._extract_content(response)
        
        # Remove boilerplate if text extraction
        if 'text' in content and self.config.enable_ml_extraction:
            from ..ml.boilerplate import BoilerplateRemover
            remover = BoilerplateRemover()
            if hasattr(response, 'text'):
                content['text']['clean_text'] = remover.extract_main_content(response.text)
        
        # Extract structured data
        structured_data = await self.extractors['structured'].extract(response)
        
        # Store results
        await self._store_result(url, content, structured_data, response)
        
        # Extract and enqueue new URLs
        if self.config.max_depth is None or depth < self.config.max_depth:
            new_urls = await self._extract_urls(url, response)
            for new_url in new_urls:
                if self._should_follow(url, new_url):
                    priority = await self._calculate_priority(new_url)
                    await self.frontier.add(new_url, depth + 1, priority)
        
        self.stats.success += 1
    
    async def _extract_content(self, response) -> Dict[str, Any]:
        """Extract content based on content type"""
        content_type = getattr(response, 'headers', {}).get('content-type', '').lower()
        url = getattr(response, 'url', '')
        
        result = {}
        
        if 'text/html' in content_type:
            result['text'] = await self.extractors['text'].extract(response)
        elif 'application/pdf' in content_type:
            result['pdf'] = await self.extractors['pdf'].extract(response)
        elif any(office_type in content_type for office_type in ['officedocument', 'msword', 'ms-excel', 'ms-powerpoint']):
            result['office'] = await self.extractors['office'].extract(response)
        elif 'image/' in content_type:
            result['image'] = await self.extractors['media'].extract_image(response)
            if self.config.extract_images:
                result['ocr'] = await self.extractors['ocr'].extract(response)
        elif 'video/' in content_type:
            result['video'] = await self.extractors['media'].extract_video(response)
        elif 'audio/' in content_type:
            result['audio'] = await self.extractors['media'].extract_audio(response)
        elif 'application/zip' in content_type or url.endswith('.zip'):
            from ..extractors.archive import ArchiveExtractor
            extractor = ArchiveExtractor()
            result['archive'] = await extractor.extract_zip(response.content)
        elif 'application/x-tar' in content_type or url.endswith(('.tar', '.tar.gz')):
            from ..extractors.archive import ArchiveExtractor
            extractor = ArchiveExtractor()
            result['archive'] = await extractor.extract_tar(response.content)
        elif 'application/epub+zip' in content_type or url.endswith('.epub'):
            from ..extractors.archive import ArchiveExtractor
            extractor = ArchiveExtractor()
            result['archive'] = await extractor.extract_epub(response.content)
        
        return result
    
    async def _extract_urls(self, base_url: str, response) -> List[str]:
        """Extract all URLs from response"""
        from .link_extractor import AdvancedLinkExtractor
        from ..engines.api_detector import APIDetector
        
        extractor = AdvancedLinkExtractor()
        urls = await extractor.extract(response, base_url)
        
        # Also detect API endpoints if HTML
        if hasattr(response, 'text') and response.text:
            api_detector = APIDetector()
            api_urls = api_detector.detect_api_endpoints(response.text, base_url)
            urls.extend(api_urls)
        
        # Normalize and deduplicate
        from .url_utils import normalize_url, deduplicate_urls
        normalized = [normalize_url(url) for url in urls]
        deduplicated = await deduplicate_urls(normalized)
        
        return deduplicated
    
    def _should_follow(self, current_url: str, target_url: str) -> bool:
        """Determine if a URL should be followed"""
        current_domain = urlparse(current_url).netloc
        target_domain = urlparse(target_url).netloc
        
        # Same domain - always follow
        if current_domain == target_domain:
            return True
        
        # Subdomain
        if self.config.follow_subdomains:
            if target_domain.endswith('.' + current_domain) or current_domain.endswith('.' + target_domain):
                return True
        
        # External
        if self.config.follow_external:
            return True
        
        return False
    
    async def _calculate_priority(self, url: str) -> float:
        """Calculate URL priority for priority queue"""
        # Base priority
        priority = 0.5
        
        # Boost for common important pages
        path = urlparse(url).path.lower()
        if any(imp in path for imp in ['/about', '/contact', '/products', '/services']):
            priority += 0.2
        
        # ML-based priority if available
        if 'classifier' in self.ml_models:
            ml_priority = await self.ml_models['classifier'].predict_importance(url)
            priority = (priority + ml_priority) / 2
        
        return priority
    
    async def _is_trap(self, url: str, response) -> bool:
        """Detect if URL is a trap"""
        from ..traps.detector import TrapDetector
        
        detector = TrapDetector()
        return await detector.is_trap(url, response)
    
    async def _is_soft_404(self, response) -> bool:
        """Detect soft 404 pages"""
        if 'soft404' not in self.ml_models:
            return False
        
        return await self.ml_models['soft404'].is_soft_404(response)
    
    def _needs_js_rendering(self, response) -> bool:
        """Determine if JS rendering is needed"""
        # Check for common JS frameworks
        if not hasattr(response, 'text'):
            return False
        content = response.text[:10000].lower()
        js_indicators = ['react', 'vue', 'angular', 'next.js', 'nuxt', '__NEXT_DATA__']
        return any(indicator in content for indicator in js_indicators)
    
    async def _is_visited(self, url: str) -> bool:
        """Check if URL has been visited"""
        if self.config.distributed:
            return await self.frontier.is_visited(url)
        return url in self.visited
    
    async def _mark_visited(self, url: str):
        """Mark URL as visited"""
        if self.config.distributed:
            await self.frontier.mark_visited(url)
        else:
            self.visited.add(url)
    
    async def _store_result(self, url: str, content: Dict, structured_data: Dict, response):
        """Store crawl results"""
        from ..distributed.storage import create_storage_backend
        
        storage = create_storage_backend(self.config)
        await storage.store(url, content, structured_data, response)
    
    async def _save_checkpoint(self):
        """Save crawl state for resumability"""
        import json
        from pathlib import Path
        
        state = {
            'processed': self.stats.processed,
            'success': self.stats.success,
            'errors': self.stats.errors,
            'visited': list(self.visited) if not self.config.distributed else [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        state_file = Path(self.config.state_file)
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Checkpoint saved to {state_file}")
    
    async def _load_checkpoint(self):
        """Load previous crawl state"""
        import json
        from pathlib import Path
        
        state_file = Path(self.config.state_file)
        
        if not state_file.exists():
            return
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            self.stats.processed = state.get('processed', 0)
            self.stats.success = state.get('success', 0)
            self.stats.errors = state.get('errors', 0)
            
            if not self.config.distributed:
                self.visited = set(state.get('visited', []))
            
            logger.info(f"Checkpoint loaded: {self.stats.processed} URLs processed")
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}")
    
    async def _generate_reports(self):
        """Generate final crawl reports"""
        from ..graph.builder import SiteGraphBuilder
        from ..graph.analyzer import GraphAnalyzer
        
        # Build site graph
        graph_builder = SiteGraphBuilder()
        graph = await graph_builder.build()
        
        # Analyze graph
        analyzer = GraphAnalyzer(graph)
        metrics = await analyzer.analyze()
        
        logger.info(f"Crawl statistics: {self.stats}")
        logger.info(f"Graph metrics: {metrics}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down DeepHarvest...")
        
        if self.js_engine:
            await self.js_engine.close()
        
        if self.fetcher:
            await self.fetcher.close()
        
        logger.info("Shutdown complete")

@dataclass
class CrawlStats:
    """Crawl statistics"""
    processed: int = 0
    success: int = 0
    errors: int = 0
    bytes_downloaded: int = 0

