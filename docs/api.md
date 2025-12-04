# API Reference

## Core Classes

### DeepHarvest

Main crawler orchestrator.

```python
from deepharvest import DeepHarvest, CrawlConfig

config = CrawlConfig(
    seed_urls=["https://example.com"],
    max_depth=5,
    enable_js=True
)

crawler = DeepHarvest(config)
await crawler.initialize()
await crawler.crawl()
await crawler.shutdown()
```

### BrowserScraper

Browser automation with Playwright.

```python
from deepharvest.browser import BrowserScraper

async with BrowserScraper() as scraper:
    result = await scraper.fetch("https://example.com", capture_screenshot=True)
    print(result.html)
    print(result.screenshot)
```

### OSINTCollector

OSINT data collection.

```python
from deepharvest.osint import OSINTCollector

collector = OSINTCollector()
await collector.initialize()
result = await collector.collect("https://example.com")
print(result['entities'])
print(result['tech_stack'])
```

## Configuration

### CrawlConfig

Configuration for crawling operations.

```python
from deepharvest.core.crawler import CrawlConfig, CrawlStrategy

config = CrawlConfig(
    seed_urls=["https://example.com"],
    strategy=CrawlStrategy.BFS,
    max_depth=5,
    concurrent_requests=10,
    enable_js=True
)
```

## Exporters

### JSONLExporter

```python
from deepharvest.exporters import JSONLExporter

exporter = JSONLExporter()
exporter.export(data, "output.jsonl")
```

### ParquetExporter

```python
from deepharvest.exporters import ParquetExporter

exporter = ParquetExporter()
exporter.export(data, "output.parquet")
```

### SQLiteExporter

```python
from deepharvest.exporters import SQLiteExporter

exporter = SQLiteExporter("database.db")
exporter.connect()
exporter.export(data)
exporter.close()
```

### VectorDBExporter

```python
from deepharvest.exporters import VectorDBExporter

exporter = VectorDBExporter(db_type='faiss', db_path='./vectordb')
exporter.initialize()
exporter.export(data, embeddings)
```

