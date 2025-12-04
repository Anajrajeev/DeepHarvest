# OSINT Mode Usage

## Overview

OSINT (Open Source Intelligence) mode collects and analyzes publicly available information from websites.

## CLI Usage

```bash
# Basic OSINT collection
deepharvest osint https://example.com

# With JSON output
deepharvest osint https://example.com --json

# With link graph export
deepharvest osint https://example.com --graph

# With screenshots
deepharvest osint https://example.com --screenshot

# Custom output directory
deepharvest osint https://example.com --output ./osint_data
```

## Python API

```python
from deepharvest.osint import OSINTCollector
from deepharvest.core.crawler import CrawlConfig

config = CrawlConfig(seed_urls=[])
collector = OSINTCollector(config)

await collector.initialize()
result = await collector.collect("https://example.com")

# Access entities
emails = result['entities']['emails']
phones = result['entities']['phones']
usernames = result['entities']['usernames']
domains = result['entities']['domains']

# Access technology stack
frameworks = result['tech_stack']['frameworks']
cms = result['tech_stack']['cms']
servers = result['tech_stack']['servers']

# Export results
collector.export_json('osint_results.json')
collector.export_graphml('link_graph.graphml')
```

## Output Format

OSINT results include:

- **Entities**: Emails, phone numbers, usernames, domains
- **Technology Stack**: Frameworks, CMS, servers, libraries
- **Link Graph**: NetworkX graph of discovered links
- **Screenshots**: Visual captures of pages

## Examples

### Collect from Multiple URLs

```python
urls = ["https://example.com", "https://example.org"]
results = await collector.collect_many(urls)
```

### Export Link Graph

```python
collector.export_graphml('graph.graphml')
```

### Get Graph Statistics

```python
graph = collector.get_graph()
stats = collector.graph_builder.get_statistics()
print(f"Nodes: {stats['nodes']}, Edges: {stats['edges']}")
```

