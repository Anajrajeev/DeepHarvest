# Architecture Overview

## System Components

```
┌─────────────────────────────────────────────────────────┐
│                    DeepHarvest Core                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   Browser   │  │    Fetcher   │  │   Frontier    │  │
│  │  (Playwright)│  │  (aiohttp)   │  │   (Queue)     │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Extractors  │  │  ML Models   │  │    Plugins    │  │
│  │  (Content)  │  │ (Classifier) │  │  (Custom)     │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Exporters  │  │    OSINT     │  │   Pipeline    │  │
│  │ (JSON/CSV)  │  │  (Entities)  │  │   (YAML)      │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

1. **URL Input** → Frontier (Queue)
2. **Frontier** → Fetcher/Browser
3. **Response** → Extractors
4. **Content** → ML Models (Classification)
5. **Results** → Exporters/Storage

## Key Modules

### Browser (`deepharvest/browser/`)

- Playwright integration
- Screenshot capture
- JavaScript rendering
- HTTP fallback

### Core (`deepharvest/core/`)

- Crawler orchestrator
- URL management
- Content extraction
- Link following

### ML (`deepharvest/ml/`)

- Page classification
- Quality scoring
- Deduplication
- Soft-404 detection

### OSINT (`deepharvest/osint/`)

- Entity extraction
- Technology detection
- Link graph building

### Plugins (`deepharvest/plugins/`)

- Auto-discovery
- Entry point loading
- Custom processing

### Exporters (`deepharvest/exporters/`)

- JSONL, Parquet, SQLite
- VectorDB (FAISS/Chroma)
- GraphML

## Async Architecture

All operations are async-first using `asyncio` and `aiohttp` for high concurrency.

## Distributed Mode

Redis-based distributed crawling with multiple workers for scalability.

