import pypandoc
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio
import os

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
            description=(
                "Converts content between different formats. Transforms input content from any supported format "
                "into the specified output format.\n\n"
                "🚨 CRITICAL REQUIREMENTS - PLEASE READ:\n"
                "1. PDF Conversion:\n"
                "   * You MUST install TeX Live BEFORE attempting PDF conversion:\n"
                "   * Ubuntu/Debian: `sudo apt-get install texlive-xetex`\n"
                "   * macOS: `brew install texlive`\n"
                "   * Windows: Install MiKTeX or TeX Live from https://miktex.org/ or https://tug.org/texlive/\n"
                "   * PDF conversion will FAIL without this installation\n\n"
                "2. File Paths - EXPLICIT REQUIREMENTS:\n"
                "   * When asked to save or convert to a file, you MUST provide:\n"
                "     - Complete directory path\n"
                "     - Filename\n"
                "     - File extension\n"
                "   * Example request: 'Write a story and save as PDF'\n"
                "   * You MUST specify: '/path/to/story.pdf' or 'C:\\Documents\\story.pdf'\n"
                "   * The tool will NOT automatically generate filenames or extensions\n\n"
                "3. File Location After Conversion:\n"
                "   * After successful conversion, the tool will display the exact path where the file is saved\n"
                "   * Look for message: 'Content successfully converted and saved to: [file_path]'\n"
                "   * You can find your converted file at the specified location\n"
                "   * If no path is specified, files may be saved in system temp directory (/tmp/ on Unix systems)\n"
                "   * For better control, always provide explicit output file paths\n\n"
                "Supported formats:\n"
                "- Basic formats: txt, html, markdown\n"
                "- Advanced formats (REQUIRE complete file paths): pdf, docx, rst, latex, epub\n\n"
                "✅ CORRECT Usage Examples:\n"
                "1. 'Convert this text to HTML' (basic conversion)\n"
                "   - Tool will show converted content\n\n"
                "2. 'Save this text as PDF at /documents/story.pdf'\n"
                "   - Correct: specifies path + filename + extension\n"
                "   - Tool will show: 'Content successfully converted and saved to: /documents/story.pdf'\n\n"
                "❌ INCORRECT Usage Examples:\n"
                "1. 'Save this as PDF in /documents/'\n"
                "   - Missing filename and extension\n"
                "2. 'Convert to PDF'\n"
                "   - Missing complete file path\n\n"
                "When requesting conversion, ALWAYS specify:\n"
                "1. The content or input file\n"
                "2. The desired output format\n"
                "3. For advanced formats: complete output path + filename + extension\n"
                "Example: 'Convert this markdown to PDF and save as /path/to/output.pdf'\n\n"
                "Note: After conversion, always check the success message for the exact file location."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contents": {
                        "type": "string",
                        "description": "The content to be converted (required if input_file not provided)"
                    },
                    "input_file": {
                        "type": "string",
                        "description": "Complete path to input file including filename and extension (e.g., '/path/to/input.md')"
                    },
                    "input_format": {
                        "type": "string",
                        "description": "Source format of the content (defaults to markdown)",
                        "default": "markdown",
                        "enum": ["markdown", "html", "pdf", "docx", "rst", "latex", "epub", "txt"]
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Desired output format (defaults to markdown)",
                        "default": "markdown",
                        "enum": ["markdown", "html", "pdf", "docx", "rst", "latex", "epub", "txt"]
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Complete path where to save the output including filename and extension (required for pdf, docx, rst, latex, epub formats)"
                    }
                },
                "oneOf": [
                    {"required": ["contents"]},
                    {"required": ["input_file"]}
                ],
                "allOf": [
                    {
                        "if": {
                            "properties": {
                                "output_format": {
                                    "enum": ["pdf", "docx", "rst", "latex", "epub"]
                                }
                            }
                        },
                        "then": {
                            "required": ["output_file"]
                        }
                    }
                ]
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

    # Extract all possible arguments
    contents = arguments.get("contents")
    input_file = arguments.get("input_file")
    output_file = arguments.get("output_file")
    output_format = arguments.get("output_format", "markdown").lower()
    input_format = arguments.get("input_format", "markdown").lower()
    
    # Validate input parameters
    if not contents and not input_file:
        raise ValueError("Either 'contents' or 'input_file' must be provided")
    
    # Define supported formats
    SUPPORTED_FORMATS = {'html', 'markdown', 'pdf', 'docx', 'rst', 'latex', 'epub', 'txt'}
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported output format: '{output_format}'. Supported formats are: {', '.join(SUPPORTED_FORMATS)}")
    
    # Validate output_file requirement for advanced formats
    ADVANCED_FORMATS = {'pdf', 'docx', 'rst', 'latex', 'epub'}
    if output_format in ADVANCED_FORMATS and not output_file:
        raise ValueError(f"output_file path is required for {output_format} format")
    
    try:
        # Prepare conversion arguments
        extra_args = []
        
        # Handle PDF-specific conversion if needed
        if output_format == "pdf":
            extra_args.extend([
                "--pdf-engine=xelatex",
                "-V", "geometry:margin=1in"
            ])
        
        # Convert content using pypandoc
        if input_file:
            if not os.path.exists(input_file):
                raise ValueError(f"Input file not found: {input_file}")
            
            if output_file:
                # Convert file to file
                converted_output = pypandoc.convert_file(
                    input_file,
                    output_format,
                    outputfile=output_file,
                    extra_args=extra_args
                )
                result_message = f"File successfully converted and saved to: {output_file}"
            else:
                # Convert file to string
                converted_output = pypandoc.convert_file(
                    input_file,
                    output_format,
                    extra_args=extra_args
                )
        else:
            if output_file:
                # Convert content to file
                pypandoc.convert_text(
                    contents,
                    output_format,
                    format=input_format,
                    outputfile=output_file,
                    extra_args=extra_args
                )
                result_message = f"Content successfully converted and saved to: {output_file}"
            else:
                # Convert content to string
                converted_output = pypandoc.convert_text(
                    contents,
                    output_format,
                    format=input_format,
                    extra_args=extra_args
                )
        
        if output_file:
            notify_with_result = result_message
        else:
            if not converted_output:
                raise ValueError(f"Conversion resulted in empty output")
            notify_with_result = (
                f'Following are the converted contents in {output_format} format.\n'
                f'Ask user if they expect to save this file. If so, provide the output_file parameter with complete path.\n'
                f'Converted Contents:\n\n{converted_output}'
            )
        
        return [
            types.TextContent(
                type="text",
                text=notify_with_result
            )
        ]
        
    except Exception as e:
        # Handle Pandoc conversion errors
        error_msg = f"Error converting {'file' if input_file else 'contents'} from {input_format} to {output_format}: {str(e)}"
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