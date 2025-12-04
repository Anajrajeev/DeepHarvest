# Browser Automation Guide

## Overview

DeepHarvest provides a high-level browser automation layer using Playwright with automatic fallback to HTTP requests.

## Basic Usage

```python
from deepharvest.browser import BrowserScraper

async with BrowserScraper() as scraper:
    result = await scraper.fetch("https://example.com")
    print(result.html)
```

## Screenshot Capture

```python
async with BrowserScraper() as scraper:
    result = await scraper.fetch(
        "https://example.com",
        capture_screenshot=True,
        screenshot_path="./screenshot.png"
    )
    
    if result.screenshot:
        with open("screenshot.png", "wb") as f:
            f.write(result.screenshot)
```

## JavaScript Rendering

```python
# With JavaScript (default)
result = await scraper.fetch("https://example.com", use_js=True)

# Without JavaScript (faster)
result = await scraper.fetch("https://example.com", use_js=False)
```

## Configuration

```python
from deepharvest.core.crawler import CrawlConfig

config = CrawlConfig(
    seed_urls=[],
    wait_for_js_ms=3000,
    handle_infinite_scroll=True
)

async with BrowserScraper(config) as scraper:
    result = await scraper.fetch("https://example.com")
```

## Advanced Features

### Custom User Agent

```python
config = CrawlConfig(seed_urls=[])
config.user_agent = "MyBot/1.0"

async with BrowserScraper(config) as scraper:
    result = await scraper.fetch("https://example.com")
```

### Headless Mode

```python
scraper = BrowserScraper(headless=True)  # Default
await scraper.initialize()
```

## Error Handling

The browser scraper automatically falls back to HTTP requests if browser automation fails:

```python
try:
    result = await scraper.fetch(url, use_js=True)
except Exception as e:
    # Automatic fallback to HTTP
    result = await scraper.fetch(url, use_js=False)
```

