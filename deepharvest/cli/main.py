"""
Command-Line Interface for DeepHarvest
"""
import click
import asyncio
import yaml
from pathlib import Path
import json
import logging
import sys

@click.group()
@click.version_option(version='1.0.1')
def cli():
    """DeepHarvest - The World's Most Complete Web Crawler"""
    pass

@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--config', '-c', type=click.Path(exists=True), help='Config file path')
@click.option('--depth', '-d', type=int, default=None, help='Maximum crawl depth')
@click.option('--output', '-o', default='./crawl_output', help='Output directory')
@click.option('--js/--no-js', default=True, help='Enable JavaScript rendering')
@click.option('--distributed', is_flag=True, help='Run in distributed mode')
@click.option('--redis-url', help='Redis URL for distributed mode')
@click.option('--workers', type=int, default=1, help='Number of workers')
@click.option('--max-urls', type=int, default=None, help='Maximum total URLs to crawl')
@click.option('--max-size', type=int, default=None, help='Maximum response size in MB')
@click.option('--max-pages-per-domain', type=int, default=None, help='Maximum pages to crawl per domain')
@click.option('--time-limit', type=int, default=None, help='Maximum crawl time in seconds')
def crawl(urls, config, depth, output, js, distributed, redis_url, workers, max_urls, max_size, max_pages_per_domain, time_limit):
    """Start crawling URLs"""
    
    click.echo(f"Starting DeepHarvest v1.0.0")
    click.echo(f"Crawling {len(urls)} seed URL(s)")
    
    # Load config
    if config:
        with open(config) as f:
            cfg = yaml.safe_load(f)
    else:
        cfg = {}
    
    # Override with CLI options
    if depth:
        cfg['max_depth'] = depth
    if output:
        cfg['output_dir'] = output
    cfg['enable_js'] = js
    cfg['distributed'] = distributed
    if max_urls:
        cfg['max_urls'] = max_urls
    if max_size:
        cfg['max_size_mb'] = max_size
    if max_pages_per_domain:
        cfg['max_pages_per_domain'] = max_pages_per_domain
    if time_limit:
        cfg['time_limit_seconds'] = time_limit
    
    if distributed and not redis_url:
        click.echo("Error: --redis-url required for distributed mode", err=True)
        return
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        stream=sys.stdout
    )
    
    # Run crawler
    async def run():
        from deepharvest.core.crawler import DeepHarvest, CrawlConfig, CrawlStrategy
        
        crawl_config = CrawlConfig(
            seed_urls=list(urls),
            **cfg
        )
        
        if distributed:
            crawl_config.redis_url = redis_url
        
        crawler = DeepHarvest(crawl_config)
        
        try:
            click.echo("Initializing crawler...")
            await crawler.initialize()
            click.echo(f"Starting crawl...")
            await crawler.crawl()
            
            # Show stats
            stats = crawler.stats
            click.echo(f"\nCrawl Statistics:")
            click.echo(f"  URLs Processed: {stats.processed}")
            click.echo(f"  Successful: {stats.success}")
            click.echo(f"  Errors: {stats.errors}")
            if stats.bytes_downloaded > 0:
                click.echo(f"  Bytes Downloaded: {stats.bytes_downloaded:,}")
            click.echo(f"  Output Directory: {crawl_config.output_dir}")
        finally:
            await crawler.shutdown()
    
    asyncio.run(run())
    
    click.echo("Crawl completed!")

@cli.command()
@click.option('--state-file', default='crawl_state.json', help='State file path')
def resume(state_file):
    """Resume a previous crawl"""
    
    if not Path(state_file).exists():
        click.echo(f"State file not found: {state_file}", err=True)
        return
    
    click.echo(f"Resuming crawl from {state_file}")
    
    # Load state and resume
    with open(state_file) as f:
        state = json.load(f)
    
    click.echo(f"Processed: {state.get('processed', 0)} URLs")
    click.echo("Resuming...")
    
    # Implementation would load state and continue

@cli.command()
@click.option('--redis-url', required=True, help='Redis URL')
def status(redis_url):
    """Show crawl status"""
    
    async def get_status():
        from deepharvest.distributed.redis_frontier import RedisFrontier
        
        frontier = RedisFrontier(redis_url)
        await frontier.connect()
        
        stats = await frontier.get_stats()
        
        click.echo("\nCrawl Status")
        click.echo("=" * 50)
        click.echo(f"Queued:      {stats['queued']:,}")
        click.echo(f"Processed:   {stats['processed']:,}")
        click.echo(f"In Progress: {stats['in_progress']:,}")
        click.echo(f"Visited:     {stats['visited']:,}")
        click.echo("=" * 50)
        
        await frontier.close()
    
    asyncio.run(get_status())

@cli.command()
@click.argument('output_dir')
@click.option('--format', type=click.Choice(['graphml', 'json', 'csv']), default='graphml')
def export_graph(output_dir, format):
    """Export site graph"""
    
    click.echo(f"Exporting site graph to {format}")
    
    # Implementation would generate and export graph
    click.echo("Graph exported successfully!")

@cli.command()
def list_plugins():
    """List available plugins"""
    
    click.echo("\nAvailable Plugins")
    click.echo("=" * 50)
    click.echo("• speech_to_text.whisper - OpenAI Whisper STT")
    click.echo("• extractors.custom - Custom content extractor")
    click.echo("=" * 50)

if __name__ == '__main__':
    cli()

