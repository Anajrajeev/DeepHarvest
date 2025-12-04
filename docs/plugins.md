# Plugin Development Guide

## Overview

DeepHarvest supports a plugin system for extending functionality. Plugins can be used for custom extractors, summarizers, downloaders, and more.

## Creating a Plugin

### Basic Plugin Structure

```python
from deepharvest.plugins.base import Plugin
from typing import Dict, Any

class MyPlugin(Plugin):
    async def initialize(self):
        """Initialize plugin"""
        pass
    
    async def process(self, url: str, response) -> Dict[str, Any]:
        """Process content"""
        html = getattr(response, 'text', '') if response else ''
        return {
            'url': url,
            'processed': True,
            'data': html[:100]
        }
    
    async def shutdown(self):
        """Cleanup resources"""
        pass
```

## Registering Plugins

### Entry Points (Recommended)

Add to `pyproject.toml`:

```toml
[project.entry-points."deepharvest.plugins"]
my_plugin = "mypackage.plugins.my_plugin:MyPlugin"
```

### Local Plugins

Place plugin files in `deepharvest/plugins/` directory.

## Using Plugins

```python
from deepharvest.plugins import PluginLoader

loader = PluginLoader()
plugins = loader.discover_plugins()
my_plugin = await loader.load_plugin('my_plugin')
result = await my_plugin.process(url, response)
```

## Plugin Types

### Extractors

Extract custom data from pages.

### Summarizers

Summarize content.

### Downloaders

Download and process files.

## Example Plugins

See `deepharvest/plugins/extractors/`, `deepharvest/plugins/summarizers/`, and `deepharvest/plugins/downloaders/` for examples.

