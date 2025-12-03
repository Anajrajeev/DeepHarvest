"""
frontier.py - URL Frontier Management
"""
import asyncio
from typing import Optional, Tuple
from .crawler import CrawlStrategy

class LocalFrontier:
    """Local in-memory frontier with BFS/DFS/Priority support"""
    def __init__(self, strategy: CrawlStrategy):
        self.strategy = strategy
        self.queue = asyncio.Queue() if strategy == CrawlStrategy.BFS else asyncio.LifoQueue()
        # Priority queue implementation
    
    async def add(self, url: str, depth: int, priority: float):
        await self.queue.put((url, depth, priority))
    
    async def get(self):
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=5.0)
        except asyncio.TimeoutError:
            return None
    
    async def mark_done(self, url: str):
        pass

