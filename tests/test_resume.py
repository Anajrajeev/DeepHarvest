"""
Test resume functionality
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from deepharvest.core.crawler import DeepHarvest, CrawlConfig, CrawlStrategy
from deepharvest.core.frontier import LocalFrontier


class TestResumeFunctionality:
    """Test resume functionality"""

    @pytest.mark.asyncio
    async def test_checkpoint_save_frontier_state(self):
        """Test that checkpoint saves frontier state"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"

            config = CrawlConfig(
                seed_urls=["https://example.com"],
                max_depth=2,
                state_file=str(state_file),
                checkpoint_interval=1,  # Save after every URL
            )

            crawler = DeepHarvest(config)
            await crawler.initialize()

            # Add some URLs to frontier manually
            await crawler.frontier.add("https://example.com/page1", depth=1, priority=0.8)
            await crawler.frontier.add("https://example.com/page2", depth=1, priority=0.9)

            # Save checkpoint
            await crawler._save_checkpoint()

            # Verify checkpoint file exists and contains frontier data
            assert state_file.exists()
            with open(state_file) as f:
                state = json.load(f)

            assert "frontier" in state
            assert len(state["frontier"]) == 2
            assert state["frontier"][0]["url"] in [
                "https://example.com/page1",
                "https://example.com/page2",
            ]
            assert "depth" in state["frontier"][0]
            assert "priority" in state["frontier"][0]

            await crawler.shutdown()

    @pytest.mark.asyncio
    async def test_checkpoint_load_frontier_state(self):
        """Test that checkpoint loads and restores frontier state"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"

            # Create a checkpoint file with frontier state
            checkpoint_data = {
                "processed": 5,
                "success": 4,
                "errors": 1,
                "visited": ["https://example.com"],
                "frontier": [
                    {"url": "https://example.com/page1", "depth": 1, "priority": 0.8},
                    {"url": "https://example.com/page2", "depth": 1, "priority": 0.9},
                ],
                "timestamp": "2024-01-01T00:00:00",
            }

            with open(state_file, "w") as f:
                json.dump(checkpoint_data, f)

            config = CrawlConfig(
                seed_urls=["https://example.com"],
                max_depth=2,
                state_file=str(state_file),
            )

            crawler = DeepHarvest(config)
            await crawler.initialize()

            # Verify frontier was restored
            assert crawler._frontier_restored is True

            # Verify visited URLs were restored
            assert "https://example.com" in crawler.visited

            # Verify stats were restored
            assert crawler.stats.processed == 5
            assert crawler.stats.success == 4
            assert crawler.stats.errors == 1

            # Verify frontier has pending URLs (check by trying to get them)
            # Note: We can't directly inspect queue, but we can verify it's not empty
            # by checking that get() returns a value
            item = await crawler.frontier.get()
            assert item is not None
            url, depth, priority = item
            assert url in ["https://example.com/page1", "https://example.com/page2"]
            assert depth == 1
            assert priority in [0.8, 0.9]

            await crawler.shutdown()

    @pytest.mark.asyncio
    async def test_resume_skips_seed_urls(self):
        """Test that resume does not re-add seed URLs if frontier is restored"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"

            # Create checkpoint with frontier state
            checkpoint_data = {
                "processed": 1,
                "success": 1,
                "errors": 0,
                "visited": ["https://example.com"],
                "frontier": [
                    {"url": "https://example.com/page1", "depth": 1, "priority": 0.8},
                ],
                "timestamp": "2024-01-01T00:00:00",
            }

            with open(state_file, "w") as f:
                json.dump(checkpoint_data, f)

            config = CrawlConfig(
                seed_urls=["https://example.com"],  # This should NOT be re-added
                max_depth=2,
                state_file=str(state_file),
            )

            crawler = DeepHarvest(config)
            await crawler.initialize()

            # Verify frontier was restored
            assert crawler._frontier_restored is True

            # Manually trigger crawl() logic check - seed URLs should not be added
            # We'll check by verifying the frontier only has the restored URL
            item = await crawler.frontier.get()
            assert item is not None
            url, depth, priority = item
            # Should be the restored URL, not the seed
            assert url == "https://example.com/page1"
            assert url != "https://example.com"  # Seed should not be in queue

            await crawler.shutdown()

    @pytest.mark.asyncio
    async def test_backward_compatibility_no_frontier(self):
        """Test that old checkpoints without frontier data still work"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"

            # Create old-style checkpoint (no frontier field)
            checkpoint_data = {
                "processed": 5,
                "success": 4,
                "errors": 1,
                "visited": ["https://example.com"],
                "timestamp": "2024-01-01T00:00:00",
            }

            with open(state_file, "w") as f:
                json.dump(checkpoint_data, f)

            config = CrawlConfig(
                seed_urls=["https://example.com"],
                max_depth=2,
                state_file=str(state_file),
            )

            crawler = DeepHarvest(config)
            await crawler.initialize()

            # Should load successfully without frontier
            assert crawler._frontier_restored is False
            assert "https://example.com" in crawler.visited
            assert crawler.stats.processed == 5

            # Seed URLs should be added normally (no frontier restored)
            # This is the old behavior

            await crawler.shutdown()

    @pytest.mark.asyncio
    async def test_distributed_mode_no_frontier_save(self):
        """Test that distributed mode does not save frontier state"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "test_state.json"

            config = CrawlConfig(
                seed_urls=["https://example.com"],
                max_depth=2,
                state_file=str(state_file),
                distributed=True,
                redis_url="redis://localhost:6379",
            )

            crawler = DeepHarvest(config)
            # Don't actually connect to Redis, just test the save logic
            # We'll mock the frontier as RedisFrontier
            from deepharvest.distributed.redis_frontier import RedisFrontier

            crawler.frontier = RedisFrontier("redis://localhost:6379")

            # Save checkpoint
            await crawler._save_checkpoint()

            # Verify checkpoint does NOT contain frontier
            assert state_file.exists()
            with open(state_file) as f:
                state = json.load(f)

            assert "frontier" not in state
            assert "visited" not in state  # Also not saved in distributed mode

    @pytest.mark.asyncio
    async def test_local_frontier_snapshot_restore(self):
        """Test LocalFrontier snapshot and restore methods"""
        frontier = LocalFrontier(CrawlStrategy.BFS)

        # Add some URLs
        await frontier.add("https://example.com/page1", depth=1, priority=0.8)
        await frontier.add("https://example.com/page2", depth=2, priority=0.9)

        # Get snapshot
        snapshot = await frontier.get_pending_snapshot()

        assert len(snapshot) == 2
        urls = [item["url"] for item in snapshot]
        assert "https://example.com/page1" in urls
        assert "https://example.com/page2" in urls

        # Verify queue still has items (snapshot should restore them)
        item = await frontier.get()
        assert item is not None

        # Create new frontier and restore
        new_frontier = LocalFrontier(CrawlStrategy.BFS)
        await new_frontier.restore_pending(snapshot)

        # Verify restored
        item1 = await new_frontier.get()
        item2 = await new_frontier.get()

        assert item1 is not None
        assert item2 is not None
        urls_restored = [item1[0], item2[0]]
        assert "https://example.com/page1" in urls_restored
        assert "https://example.com/page2" in urls_restored
