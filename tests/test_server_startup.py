"""Regression tests for the MCP server startup contract."""

import sys
import tomllib
from pathlib import Path

import pytest
from mcp import Client, ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_mcp_dependency_uses_sdk_v2():
    """Keep fresh installs on the SDK API implemented by this release."""
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    dependencies = tomllib.loads(pyproject.read_text())["project"]["dependencies"]

    assert "mcp>=2,<3" in dependencies
    assert "jsonschema>=4.25.1" in dependencies


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
            called = await session.call_tool(
                "convert-contents",
                {"contents": "# Hello", "input_format": "markdown", "output_format": "html"},
            )

    assert initialized.server_info.name == "mcp-pandoc"
    assert initialized.server_info.version == "0.11.0"
    assert [tool.name for tool in tools.tools] == ["convert-contents"]
    assert called.is_error is False
    assert '<h1 id="hello">Hello</h1>' in called.content[0].text


@pytest.mark.asyncio
async def test_modern_client_preserves_tool_contract(tmp_path):
    """Exercise the SDK v2 protocol path without changing the public tool."""
    from mcp_pandoc.server import server

    async with Client(server, raise_exceptions=True) as client:
        tools = await client.list_tools()
        valid = await client.call_tool(
            "convert-contents",
            {"contents": "# Hello", "input_format": "markdown", "output_format": "html"},
        )
        invalid = await client.call_tool(
            "convert-contents",
            {"contents": "x", "unexpected": True},
        )
        missing = await client.call_tool("convert-contents", {})
        txt_output = tmp_path / "output.txt"
        txt = await client.call_tool(
            "convert-contents",
            {
                "input_file": str(Path(__file__).parents[1] / "testing/input/test.md"),
                "input_format": "markdown",
                "output_format": "txt",
                "output_file": str(txt_output),
            },
        )

    tool = tools.tools[0]
    assert tool.name == "convert-contents"
    assert tool.input_schema["additionalProperties"] is False
    assert not ({"oneOf", "allOf", "anyOf"} & tool.input_schema.keys())
    assert valid.is_error is False
    assert '<h1 id="hello">Hello</h1>' in valid.content[0].text
    assert invalid.is_error is True
    assert invalid.content[0].text == (
        "Input validation error: Additional properties are not allowed ('unexpected' was unexpected)"
    )
    assert missing.is_error is True
    assert missing.content[0].text == "Missing arguments"
    assert txt.is_error is False
    assert "MCP-Pandoc Test Document" in txt_output.read_text(encoding="utf-8")
