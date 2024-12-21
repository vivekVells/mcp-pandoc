import pypandoc
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

server = Server("mcp-pandoc")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="convert-contents",
            description="Converts content between different formats. Transforms input content from any supported format into the specified output format. Supported output formats include HTML, Markdown and Docx. Use this tool to seamlessly convert between different document and content representations while preserving formatting and structure.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contents": {"type": "string"},
                    "output_format": {"type": "string"},
                },
                "required": ["contents", "output_format"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:    
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name not in ["convert-contents"]:
        raise ValueError(f"Unknown tool: {name}")
    
    print(arguments)

    if not arguments:
        raise ValueError("Missing arguments")
    

    contents = arguments.get("contents")
    output_format = arguments.get("output_format", "").lower()
    
    # Validate required parameters
    if not contents:
        raise ValueError("Missing required parameter: 'contents'")
    if not output_format:
        raise ValueError("Missing required parameter: 'output_format'")
    
    # Validate supported output formats
    SUPPORTED_FORMATS = {'html', 'markdown', 'docx'}
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported output format: '{output_format}'. Supported formats are: {', '.join(SUPPORTED_FORMATS)}")
    
    try:
        # Convert content using Pandoc        
        converted_output = pypandoc.convert_text(contents, output_format, format='markdown')

        # doc = pandoc.read(contents, format="markdown")
        # converted_output = pandoc.write(doc, format=output_format)
        notify_with_result = f'Followings are the converted contents in {output_format} format. \n Ask user if they expects to save this file. If so, they can also use "Filesystem MCP Server" \n Converted Contents: \n\n{converted_output}'
        
        if not converted_output:
            raise ValueError(f"Conversion resulted in empty output")
        
        return [
            types.TextContent(
                type="text",
                text=notify_with_result
            )
        ]
        
    except Exception as e:
        # Handle Pandoc conversion errors
        error_msg = f"Error converting contents: '{contents}' to {output_format}: {str(e)}"
        raise ValueError(error_msg)

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-pandoc",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )