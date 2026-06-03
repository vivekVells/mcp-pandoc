"""mcp_pandoc package initialization."""
import asyncio
import os

from . import server
from .http_server import run_http


def main():
    """Run the mcp-pandoc server."""
    transport = os.environ.get("MCP_PANDOC_TRANSPORT", "stdio")
    if transport == "http":
        asyncio.run(run_http())
    else:
        asyncio.run(server.main())


__all__ = ["main", "server"]
