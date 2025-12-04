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

## Getting Help

- Check logs for detailed error messages
- Review configuration settings
- Test with simple URLs first
- Check GitHub issues for known problems

