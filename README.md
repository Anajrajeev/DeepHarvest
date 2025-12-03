# DeepHarvest

**A Complete, Resilient, Multilingual Web Crawler**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-enabled-blue)](https://www.docker.com/)

## Features

### Core Capabilities

- **Complete Coverage**: Crawls entire websites including all subpages
- **All Content Types**: HTML, PDF, DOCX, PPTX, XLSX, images, audio, video
- **JavaScript Support**: Full SPA support with Playwright
- **Multilingual**: Handles all languages, encodings, and scripts
- **Distributed**: Redis-based distributed crawling with multiple workers
- **Resumable**: Checkpoint and resume interrupted crawls
- **Intelligent**: ML-based trap detection, content extraction, deduplication

### Advanced Features

- **Smart Trap Detection**: Calendar, pagination, session ID, faceted navigation
- **ML Content Extraction**: Page classification, soft-404 detection, quality scoring
- **Advanced URL Management**: SimHash, MinHash, LSH deduplication
- **Site Graph Analysis**: PageRank, clustering, GraphML export
- **Observability**: Prometheus metrics, Grafana dashboards
- **Extensible**: Plugin system for custom extractors

## Quick Start

### Installation

```bash
pip install deepharvest
```

### Basic Usage

```bash
# Simple crawl
deepharvest crawl https://example.com --depth 5 --output ./output

# With JavaScript
deepharvest crawl https://example.com --js --depth 3

# Distributed mode
deepharvest crawl https://example.com --distributed --redis-url redis://localhost:6379 --workers 5
```

### Python API

```python
import asyncio
from deepharvest import DeepHarvest, CrawlConfig

async def main():
    config = CrawlConfig(
        seed_urls=["https://example.com"],
        max_depth=5,
        enable_js=True
    )
    
    crawler = DeepHarvest(config)
    await crawler.initialize()
    await crawler.crawl()
    await crawler.shutdown()

asyncio.run(main())
```

## Installation

### From PyPI

```bash
pip install deepharvest
```

### From Source

```bash
git clone https://github.com/deepharvest/deepharvest
cd deepharvest
pip install -e .
```

### Using Docker

```bash
docker-compose up
```

## Documentation

Documentation is available in the repository. Please refer to the code comments and examples for usage.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DeepHarvest Core                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Frontier   │  │   Fetcher    │  │  JS Renderer  │  │
│  │  (BFS/DFS)  │  │  (HTTP/2/3)  │  │  (Playwright) │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Extractors  │  │  Trap Det.   │  │  URL Dedup    │  │
│  │  (50+ fmt)  │  │  (ML+Rules)  │  │  (SimHash)    │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
├─────────────────────────────────────────────────────────┤
│                  Distributed Layer                       │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐            │
│  │  Redis   │  │  Workers  │  │ Storage  │            │
│  │ Frontier │  │  (N proc) │  │ (S3/FS)  │            │
│  └──────────┘  └───────────┘  └──────────┘            │
└─────────────────────────────────────────────────────────┘
```

## How It Works

DeepHarvest operates as a distributed web crawling system that systematically discovers, fetches, and extracts content from websites. The architecture follows a modular design with clear separation of concerns.

### Core Workflow

1. **Initialization**: The crawler initializes components (frontier, fetcher, extractors, ML models) based on configuration.

2. **URL Management (Frontier)**: A priority queue manages URLs to be crawled. Supports BFS, DFS, and priority-based strategies. In distributed mode, Redis coordinates URL distribution across workers.

3. **Content Fetching**: The fetcher downloads web pages with retry logic, timeout handling, and rate limiting. Supports HTTP/2 and HTTP/3 protocols.

4. **HTML Parsing**: Multi-strategy parser with fallback chain (lxml → html5lib → html.parser) ensures robust parsing of malformed HTML.

5. **JavaScript Rendering**: For Single Page Applications (SPAs), Playwright renders pages, executes JavaScript, handles infinite scroll, and captures the final DOM state.

6. **Content Extraction**: Specialized extractors process different content types:
   - **Text**: HTML text extraction with boilerplate removal
   - **Documents**: PDF, DOCX, PPTX, XLSX text extraction
   - **Media**: Image metadata, OCR, audio transcription, video metadata
   - **Structured Data**: JSON-LD, Microdata, OpenGraph, Schema.org

7. **Link Discovery**: Advanced link extractor finds URLs from multiple sources:
   - HTML attributes (href, src, srcset)
   - JavaScript code (router.push, window.location)
   - Structured data (JSON-LD, Microdata)
   - Meta tags and data URIs

8. **Deduplication**: Three-tier deduplication system:
   - **SHA256**: Exact URL/content duplicates
   - **SimHash**: Near-duplicate detection (64-bit hashing)
   - **MinHash LSH**: Scalable similarity search for large datasets

9. **Trap Detection**: ML and rule-based detection prevents infinite loops from:
   - Calendar-based URLs (date patterns)
   - Session ID parameters
   - Pagination traps
   - Query parameter explosions

10. **Storage**: Extracted content is stored with metadata. Supports filesystem, S3, and PostgreSQL backends.

### Distributed Architecture

In distributed mode, multiple workers share a Redis-based frontier. Each worker:
- Pulls URLs from the shared queue
- Processes pages independently
- Respects per-host concurrency limits
- Reports metrics to centralized monitoring

This enables linear scaling: N workers process approximately N times the throughput of a single worker.

### Resilience Features

- **Parser Fallback**: Automatic fallback between parsers when HTML is malformed
- **Network Resilience**: Exponential backoff retry, timeout handling, proxy support
- **Memory Management**: Streaming for large files, memory guards per worker
- **Checkpointing**: Periodic state saves enable resuming interrupted crawls
- **Error Taxonomy**: Structured error handling with detailed reporting

### Machine Learning Integration

- **Page Classification**: Identifies page types (article, product, forum, etc.) for intelligent prioritization
- **Soft-404 Detection**: Identifies pages that return 200 but are effectively 404s
- **Quality Scoring**: ML-based content quality assessment
- **Trap Detection**: Pattern recognition for crawler traps

### Multilingual Support

- Automatic encoding detection (charset_normalizer, chardet)
- Language detection (langdetect)
- CJK (Chinese, Japanese, Korean) text processing
- RTL (Right-to-Left) language support
- Unicode normalization

## Use Cases

- **Research**: Academic data collection and analysis
- **SEO**: Site auditing and competitive analysis
- **Media Monitoring**: News and content aggregation
- **Business Intelligence**: Market research and data mining
- **AI Training**: Dataset creation for ML models
- **Analytics**: Web structure and link analysis

## Configuration

Create a `config.yaml`:

```yaml
seed_urls:
  - https://example.com
max_depth: 5
enable_js: true
distributed: true
redis_url: redis://localhost:6379
extractors:
  - text
  - pdf
  - office
  - images
ml_features:
  trap_detection: true
  soft404_detection: true
  content_extraction: true
```

Run with config:

```bash
deepharvest crawl --config config.yaml
```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# With coverage
pytest --cov=deepharvest tests/
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache-2.0 License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built with amazing open-source tools:

- Playwright for JavaScript rendering
- BeautifulSoup & lxml for HTML parsing
- PyMuPDF for PDF extraction
- Redis for distributed coordination
- scikit-learn for ML models

---

Contributions are welcome anytime! This project was initially developed by a single contributor, and we're excited to welcome new contributors to help make DeepHarvest even better.

