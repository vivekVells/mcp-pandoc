import pypandoc
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import subprocess

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
            description="Converts content between different formats. Transforms input content from any supported format into the specified output format. Supported output formats include HTML, Markdown, PDF and Docx. Use this tool to seamlessly convert between different document and content representations while preserving formatting and structure.",
            inputSchema={
                "type": "object",
                "properties": {
                    "contents": {"type": "string"},
                    "output_format": {"type": "string"},
                    "output_file_name": {"type": "string"},
                    "output_file_path": {"type": "string"}
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
    output_file_path = arguments.get("output_file_path")
    output_file_name = arguments.get("output_file_name")
    output_format = arguments.get("output_format", "").lower()
    
    # Validate required parameters
    if not contents:
        raise ValueError("Missing required parameter: 'contents'")
    if not output_format:
        raise ValueError("Missing required parameter: 'output_format'")
    
    # Validate supported output formats
    SUPPORTED_FORMATS = {'html', 'markdown', 'docx', 'pdf'}
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported output format: '{output_format}'. Supported formats are: {', '.join(SUPPORTED_FORMATS)}")
    
    try:       
        if output_format in ['html', 'markdown']:
            converted_output = pypandoc.convert_text(contents, output_format, format='markdown')
            if not converted_output:
                raise ValueError("Conversion resulted in empty output")
            notify_with_result = (f'Following are the converted contents in {output_format} format.\n'
                                'Ask user if they expect to save this file. If so, they can also use "Filesystem MCP Server".\n'
                                f'Converted Contents:\n\n{converted_output}')
        
        elif output_format in ['docx', 'pdf']:
            if output_file_path is None:
                raise ValueError("Requires output file path to store the content!")
            if output_file_name is None:
                raise ValueError("Requires output file name to store the content properly!")
            full_path = f"{output_file_path.rstrip('/')}/{output_file_name if output_file_name.endswith(f'.{output_format}') else f'{output_file_name}.{output_format}'}"

            subprocess.run(['pandoc', '-f', 'markdown', '-o', full_path, '--pdf-engine=weasyprint'], input=contents.encode(), check=True)
            notify_with_result = f'Followings are the converted contents in {output_format} format. Converted contents are stored in {output_format} is stored in {full_path}'

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