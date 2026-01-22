# Troubleshooting Guide

## Common Issues

### Playwright Installation

**Problem**: `playwright` not found

**Solution**:
```bash
pip install playwright
playwright install chromium
```

### Memory Issues

**Problem**: Out of memory during large crawls

**Solution**:
- Reduce `concurrent_requests` in config
- Enable `max_urls` limit
- Use distributed mode with multiple workers

### Encoding Errors

**Problem**: Unicode decode errors

**Solution**: DeepHarvest automatically handles encoding detection. If issues persist, check the source website encoding.

### Timeout Errors

**Problem**: Requests timing out

**Solution**:
- Increase timeout in fetcher configuration
- Check network connectivity
- Reduce `concurrent_requests`

### Plugin Loading Errors

**Problem**: Plugins not loading

**Solution**:
- Check entry points in `pyproject.toml`
- Verify plugin class inherits from `Plugin`
- Check plugin initialization code

## Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Resume Functionality

### How Resume Works

DeepHarvest saves checkpoint state periodically (default: every 100 URLs) to enable resuming interrupted crawls.

**What is saved:**
- Processed/success/error statistics
- Visited URLs (prevents re-crawling)
- Pending frontier queue (URLs waiting to be crawled)
- Timestamp

**What is restored:**
- All visited URLs are restored to skip duplicates
- Pending URLs are restored to the frontier queue
- Statistics are restored for accurate reporting
- Seed URLs are automatically skipped if frontier is restored

**Limitations:**
- Resume only works in **local mode** (not distributed mode)
- Distributed mode relies on Redis persistence instead
- Configuration must match the original crawl (or be compatible)
- Checkpoint files are JSON and can be manually inspected/edited if needed

### Resume Usage

```bash
# Basic resume
deepharvest resume --state-file crawl_state.json

# Resume with different output directory
deepharvest resume --state-file crawl_state.json --output ./new_output

# Resume with config file
deepharvest resume --state-file crawl_state.json --config config.yaml
```

### Troubleshooting Resume

**Problem**: Resume doesn't continue from where it left off

**Solution**: 
- Ensure you're using local mode (not distributed)
- Check that the checkpoint file exists and is valid JSON
- Verify the checkpoint contains a "frontier" field with pending URLs
- Old checkpoints without frontier data will still work but won't restore pending URLs

**Problem**: Seed URLs are re-added during resume

**Solution**: This is expected behavior if the checkpoint doesn't contain frontier data (old checkpoints). New checkpoints automatically skip seed URLs when frontier is restored.

## Getting Help

- Check logs for detailed error messages
- Review configuration settings
- Test with simple URLs first
- Check GitHub issues for known problems

