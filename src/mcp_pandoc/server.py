import pypandoc
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio
import os
import sys
import subprocess
import tempfile
import shutil
import hashlib
import re
import json
import yaml

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
                "Supported formats:"
                "- Basic: txt, html, markdown, ipynb, odt"
                "- Advanced (REQUIRE complete file paths): pdf, docx, rst, latex, epub"
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
                "🎨 DOCX STYLING (NEW FEATURE):\n"
                "4. Custom DOCX Styling with Reference Documents:\n"
                "   * Use reference_doc parameter to apply professional styling to DOCX output\n"
                "   * Create custom templates with your branding, fonts, and formatting\n"
                "   * Perfect for corporate reports, academic papers, and professional documents\n"
                "   * Example: 'Convert this report to DOCX using /templates/corporate-style.docx as reference and save as /reports/Q4-report.docx'\n\n"
                "🎯 PANDOC FILTERS (NEW FEATURE):\n"
                "5. Pandoc Filter Support:\n"
                "   * Use filters parameter to apply custom Pandoc filters during conversion\n"
                "   * Filters are Python scripts that modify document content during processing\n"
                "   * Perfect for Mermaid diagram conversion, custom styling, and content transformation\n"
                "   * Example: 'Convert this markdown with mermaid diagrams to DOCX using filters=[\"./filters/mermaid-to-png-vibrant.py\"] and save as /reports/diagram-report.docx'\n\n"
                "📋 Creating Reference Documents:\n"
                "   * Generate template: pandoc -o template.docx --print-default-data-file reference.docx\n"
                "   * Customize in Word/LibreOffice: fonts, colors, headers, margins\n"
                "   * Use for consistent branding across all documents\n\n"
                "📋 Filter Requirements:\n"
                "   * Filters must be executable Python scripts\n"
                "   * Use absolute paths or paths relative to current working directory\n"
                "   * Filters are applied in the order specified\n"
                "   * Common filters: mermaid conversion, color processing, table formatting\n\n"
                "📄 Defaults File Support (NEW FEATURE):\n"
                "7. Pandoc Defaults File Support:\n"
                "   * Use defaults_file parameter to specify a YAML configuration file\n"
                "   * Similar to using pandoc -d option in the command line\n"
                "   * Allows setting multiple options in a single file\n"
                "   * Options in the defaults file can include filters, reference-doc, and other Pandoc options\n"
                "   * Example: 'Convert this markdown to DOCX using defaults_file=\"/path/to/defaults.yaml\" and save as /reports/report.docx'\n\n"
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
                        "enum": ["markdown", "html", "pdf", "docx", "rst", "latex", "epub", "txt", "ipynb", "odt"]
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Desired output format (defaults to markdown)",
                        "default": "markdown",
                        "enum": ["markdown", "html", "pdf", "docx", "rst", "latex", "epub", "txt", "ipynb", "odt"]
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Complete path where to save the output including filename and extension (required for pdf, docx, rst, latex, epub formats)"
                    },
                    "reference_doc": {
                        "type": "string",
                        "description": "Path to a reference document to use for styling (supported for docx output format)"
                    },
                    "filters": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Pandoc filter paths to apply during conversion. Filters are applied in the order specified."
                    },
                    "defaults_file": {
                        "type": "string",
                        "description": "Path to a Pandoc defaults file (YAML) containing conversion options. Similar to using pandoc -d option."
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
    reference_doc = arguments.get("reference_doc")
    filters = arguments.get("filters", [])
    defaults_file = arguments.get("defaults_file")
    
    # Validate input parameters
    if not contents and not input_file:
        raise ValueError("Either 'contents' or 'input_file' must be provided")
    
    # Validate reference_doc if provided
    if reference_doc:
        if output_format != "docx":
            raise ValueError("reference_doc parameter is only supported for docx output format")
        if not os.path.exists(reference_doc):
            raise ValueError(f"Reference document not found: {reference_doc}")
    
    # Validate defaults_file if provided
    if defaults_file:
        if not os.path.exists(defaults_file):
            raise ValueError(f"Defaults file not found: {defaults_file}")
        
        # Check if it's a valid YAML file and readable
        try:
            with open(defaults_file, 'r') as f:
                yaml_content = yaml.safe_load(f)
            
            # Validate the YAML structure
            if not isinstance(yaml_content, dict):
                raise ValueError(f"Invalid defaults file format: {defaults_file} - must be a YAML dictionary")
            
            # Check if the defaults file specifies an output format that conflicts with the requested format
            if 'to' in yaml_content and yaml_content['to'] != output_format:
                print(f"Warning: Defaults file specifies output format '{yaml_content['to']}' but requested format is '{output_format}'. Using requested format.")
                
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing defaults file {defaults_file}: {str(e)}")
        except PermissionError:
            raise ValueError(f"Permission denied when reading defaults file: {defaults_file}")
        except Exception as e:
            raise ValueError(f"Error reading defaults file {defaults_file}: {str(e)}")
    
    # Define supported formats
    SUPPORTED_FORMATS = {'html', 'markdown', 'pdf', 'docx', 'rst', 'latex', 'epub', 'txt', 'ipynb', 'odt'}
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported output format: '{output_format}'. Supported formats are: {', '.join(SUPPORTED_FORMATS)}")
    
    # Validate output_file requirement for advanced formats
    ADVANCED_FORMATS = {'pdf', 'docx', 'rst', 'latex', 'epub'}
    if output_format in ADVANCED_FORMATS and not output_file:
        raise ValueError(f"output_file path is required for {output_format} format")
    
    # Validate filters if provided
    if filters:
        if not isinstance(filters, list):
            raise ValueError("filters parameter must be an array of strings")
        
        for filter_path in filters:
            if not isinstance(filter_path, str):
                raise ValueError("Each filter must be a string path")
    
    def resolve_filter_path(filter_path, defaults_file=None):
        """Resolve a filter path by trying multiple possible locations.
        
        Args:
            filter_path: The original filter path (absolute or relative)
            defaults_file: Optional path to the defaults file for context
            
        Returns:
            Resolved absolute path to the filter if found, or None if not found
        """
        # If it's already an absolute path, just use it
        if os.path.isabs(filter_path):
            paths = [filter_path]
        else:
            # Try multiple locations for relative paths
            paths = [
                # 1. Relative to current working directory
                os.path.abspath(filter_path),
                
                # 2. Relative to the defaults file directory (if provided)
                os.path.join(os.path.dirname(os.path.abspath(defaults_file)), filter_path) if defaults_file else None,
                
                # 3. Relative to the .pandoc/filters directory
                os.path.join(os.path.expanduser("~"), ".pandoc", "filters", os.path.basename(filter_path))
            ]
            # Remove None entries
            paths = [p for p in paths if p]
        
        # Try each path
        for path in paths:
            if os.path.exists(path):
                # Check if executable and try to make it executable if not
                if not os.access(path, os.X_OK):
                    try:
                        os.chmod(path, os.stat(path).st_mode | 0o111)
                        print(f"Made filter executable: {path}")
                    except Exception as e:
                        print(f"Warning: Could not make filter executable: {path} - {str(e)}")
                        continue
                
                print(f"Using filter: {path}")
                return path
                
        return None
    
    def validate_filters(filters, defaults_file=None):
        """Validate filter paths and ensure they exist and are executable."""
        validated_filters = []
        
        for filter_path in filters:
            resolved_path = resolve_filter_path(filter_path, defaults_file)
            if resolved_path:
                validated_filters.append(resolved_path)
            else:
                raise ValueError(f"Filter not found in any of the searched locations: {filter_path}")
        
        return validated_filters
    
    def format_result_info(filters=None, defaults_file=None, validated_filters=None):
        """Format filter and defaults file information for result messages."""
        filter_info = ""
        defaults_info = ""
        
        if filters and validated_filters:
            filter_names = [os.path.basename(f) for f in validated_filters]
            filter_info = f" with filters: {', '.join(filter_names)}"
        
        if defaults_file:
            defaults_basename = os.path.basename(defaults_file)
            defaults_info = f" using defaults file: {defaults_basename}"
            
        return filter_info, defaults_info
    
    try:
        # Prepare conversion arguments
        extra_args = []
        
        # Add defaults file if provided - ensure it's properly formatted for Pandoc
        if defaults_file:
            # Make sure the path is absolute
            defaults_file_abs = os.path.abspath(defaults_file)
            extra_args.extend(["--defaults", defaults_file_abs])
        
        # Set environment variables for filters
        env = os.environ.copy()
        if output_file:
            # Set PANDOC_OUTPUT_DIR to the directory of the output file
            output_dir = os.path.dirname(os.path.abspath(output_file))
            env["PANDOC_OUTPUT_DIR"] = output_dir
        else:
            output_dir = None
        
        # Validate filters once and reuse the result
        validated_filters = validate_filters(filters, defaults_file) if filters else []
        
        # Handle filter arguments
        for filter_path in validated_filters:
            extra_args.extend(["--filter", filter_path])
        
        # Handle PDF-specific conversion if needed
        if output_format == "pdf":
            extra_args.extend([
                "--pdf-engine=xelatex",
                "-V", "geometry:margin=1in"
            ])
        
        # Handle reference doc for docx format
        if reference_doc and output_format == "docx":
            extra_args.extend([
                "--reference-doc", reference_doc
            ])
        
        # No special processing needed for content
        
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
                
                # Create result message with filter and defaults information
                filter_info, defaults_info = format_result_info(filters, defaults_file, validated_filters)
                result_message = f"File successfully converted{filter_info}{defaults_info} and saved to: {output_file}"
            else:
                # Convert file to string
                converted_output = pypandoc.convert_file(
                    input_file,
                    output_format,
                    extra_args=extra_args
                )
        else:
            # No special processing needed for content
            
            if output_file:
                # Convert content to file
                pypandoc.convert_text(
                    contents,
                    output_format,
                    format=input_format,
                    outputfile=output_file,
                    extra_args=extra_args
                )
                
                # Create result message with filter and defaults information
                filter_info, defaults_info = format_result_info(filters, defaults_file, validated_filters)
                result_message = f"Content successfully converted{filter_info}{defaults_info} and saved to: {output_file}"
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
            
            # Add filter and defaults information to the notification
            filter_info, defaults_info = format_result_info(filters, defaults_file, validated_filters)
            # Adjust format for inline display
            if filter_info:
                filter_info = f" (with filters: {', '.join([os.path.basename(f) for f in validated_filters])})"
            if defaults_info:
                defaults_info = f" (using defaults file: {os.path.basename(defaults_file)})"
            
            notify_with_result = (
                f'Following are the converted contents in {output_format} format{filter_info}{defaults_info}.\n'
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
        error_prefix = "Error converting"
        error_details = str(e)
        
        if "Filter not found" in error_details or "Filter is not executable" in error_details:
            error_prefix = "Filter error during conversion"
        elif "defaults" in error_details and defaults_file:
            error_prefix = "Defaults file error during conversion"
            # Add more context about the defaults file
            error_details += f" (defaults file: {defaults_file})"
        elif "pandoc" in error_details.lower() and "not found" in error_details.lower():
            error_prefix = "Pandoc executable not found"
            error_details = "Please ensure Pandoc is installed and available in your PATH"
        
        error_msg = f"{error_prefix} {'file' if input_file else 'contents'} from {input_format} to {output_format}: {error_details}"
        raise ValueError(error_msg)

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-pandoc",
                server_version="0.7.0",  # Updated version with defaults file support
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
