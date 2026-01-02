
import asyncio
import click
import json
from .sdk import ConfigSDK, ComputeScope

@click.group()
def cli():
    """Polyglot Config SDK CLI"""
    pass

@cli.command()
def show():
    """Show resolved configuration"""
    async def _run():
        try:
            sdk = await ConfigSDK.initialize()
            resolved = await sdk.get_resolved(ComputeScope.STARTUP)
            print(json.dumps(resolved, indent=2))
        except Exception as e:
            print(f"Error: {e}")
            exit(1)
            
    asyncio.run(_run())

@cli.command()
@click.argument('template')
@click.option('--allow-errors', is_flag=True, help='Return original string on resolution failure')
def resolve(template, allow_errors):
    """Resolve a specific template string"""
    async def _run():
        try:
            # sdk = await ConfigSDK.initialize()
            # Mock implementation
            print(f"Resolving {template}... (Mock)")
        except Exception as e:
            if allow_errors:
                print(template)
            else:
                print(f"Error: {e}")
                exit(1)

    asyncio.run(_run())

if __name__ == '__main__':
    cli()
