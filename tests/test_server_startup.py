"""Regression tests for the MCP server startup contract."""

import sys
import tomllib
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_mcp_dependency_excludes_sdk_v2():
    """Keep fresh installs on the SDK API implemented by this release."""
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    dependencies = tomllib.loads(pyproject.read_text())["project"]["dependencies"]

    assert "mcp>=1.2.1,<2" in dependencies


@pytest.mark.asyncio
async def test_stdio_server_initializes_and_lists_tool():
    """Start the real entry point and complete the MCP handshake."""
    params = StdioServerParameters(
        command=sys.executable,
        args=["-c", "from mcp_pandoc import main; main()"],
    )

    async with stdio_client(params) as streams:
        async with ClientSession(*streams) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()

    assert initialized.serverInfo.name == "mcp-pandoc"
    assert initialized.serverInfo.version == "0.8.2"
    assert [tool.name for tool in tools.tools] == ["convert-contents"]
