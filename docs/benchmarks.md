# Benchmarks

## Running Benchmarks

```bash
# Run all benchmarks
python benchmarks/run_benchmarks.py

# With custom URLs
python benchmarks/run_benchmarks.py --urls https://example.com https://example.org

# Custom output directory
python benchmarks/run_benchmarks.py --output ./my_benchmarks
```

## Benchmark Types

### Scrape Speed

Measures HTML scraping speed in URLs per second.

### Playwright vs aiohttp

Compares performance between Playwright (with JS) and aiohttp (without JS).

### Extraction Quality

Measures content extraction quality scores.

### Resource Usage

Monitors CPU and memory usage under load.

### Async vs Sync

Compares async and synchronous request performance.

## Results

Benchmark results are saved as:

- Markdown report: `benchmark_report_YYYYMMDD_HHMMSS.md`
- JSON data: `benchmark_results_YYYYMMDD_HHMMSS.json`

## Example Results

```
=== Benchmark: Scrape Speed ===
URLs: 3, Iterations: 3
  Iteration 1: 2.34s
  Iteration 2: 2.12s
  Iteration 3: 2.45s
Average: 2.30s
URLs per second: 1.30
```

