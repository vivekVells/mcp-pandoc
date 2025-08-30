"""mcp_pandoc package initialization."""
import asyncio

from . import server


def main():
    """Run the mcp-pandoc server."""
    asyncio.run(server.main())

# Optionally expose other important items at package level
__all__ = ['main', 'server']
