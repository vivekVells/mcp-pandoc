"""mcp-pandoc server module."""
import os
import uuid
from typing import Annotated, Literal

import pypandoc
import yaml
from mcp.server import FastMCP
from pydantic import Field

server = FastMCP(
    name="mcp-pandoc",
    stateless_http=False,
)

TRANSPORT = os.environ.get("MCP_PANDOC_TRANSPORT", "stdio")

FORMATS = Literal["markdown", "html", "pdf", "docx", "rst", "latex", "epub", "txt", "ipynb", "odt"]

_STDIO_DESCRIPTION = (
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
    "   * Example: 'Convert this report to DOCX using /templates/corporate-style.docx as reference "
    "and save as /reports/Q4-report.docx'\n\n"
    "🎯 PANDOC FILTERS (NEW FEATURE):\n"
    "5. Pandoc Filter Support:\n"
    "   * Use filters parameter to apply custom Pandoc filters during conversion\n"
    "   * Filters are Python scripts that modify document content during processing\n"
    "   * Perfect for Mermaid diagram conversion, custom styling, and content transformation\n"
    "   * Example: 'Convert this markdown with mermaid diagrams to DOCX using "
    "filters=[\"./filters/mermaid-to-png-vibrant.py\"] and save as /reports/diagram-report.docx'\n\n"
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
    "   * Example: 'Convert this markdown to DOCX using defaults_file=\"/path/to/defaults.yaml\" "
    "and save as /reports/report.docx'\n\n"
    "Note: After conversion, always check the success message for the exact file location."
)

_HTTP_DESCRIPTION = (
    "Converts content between different formats. Transforms input content from any supported format "
    "into the specified output format.\n\n"
    "📡 HTTP Transport Mode:\n"
    "   * This server runs in HTTP mode with Streamable HTTP transport.\n"
    "   * For file input: first call `create_upload_session` to get an upload URL, "
    "POST your file to that URL, then use the returned `uploaded_file_id` with this tool.\n"
    "   * For file output: set `return_download_url=true`. The response will include "
    "a full download URL. GET that URL to retrieve the file.\n"
    "   * For reference documents, filters, or defaults files: upload them via `create_upload_session` "
    "first, then pass the returned file IDs to `reference_doc_id`, `filter_ids`, or `defaults_file_id`.\n"
    "   * Upload and download URLs are returned as full URLs (including scheme and host). "
    "No additional auth token is needed — the FILE-ID in the URL path acts as the access key.\n"
    "   * Example workflow:\n"
    "     1. Call `create_upload_session(filename='report.md')` → returns `{\"upload_url\": \"https://.../upload/xxx\", \"uploaded_file_id\": \"xxx\"}`\n"
    "     2. POST your file to the `upload_url`\n"
    "     3. Call this tool with `uploaded_file_id=\"xxx\"` and `return_download_url=true`\n"
    "     4. Response includes `download_url` — GET it to download the result\n\n"
    "Supported formats: markdown, html, pdf, docx, rst, latex, epub, txt, ipynb, odt"
)

CONVERT_DESCRIPTION = _HTTP_DESCRIPTION if TRANSPORT == "http" else _STDIO_DESCRIPTION


def _get_base_url(ctx=None) -> str:
    """Get the base URL from the request context or env vars."""
    if ctx is not None:
        try:
            req = ctx.request_context.request
            if req is not None:
                scheme = req.headers.get("x-forwarded-proto", req.url.scheme)
                host = req.headers.get("x-forwarded-host", req.headers.get("host", ""))
                if host:
                    return f"{scheme}://{host}"
        except Exception:
            pass
    base_url = os.environ.get("MCP_PANDOC_BASE_URL", "")
    if not base_url:
        port = os.environ.get("MCP_PANDOC_PORT", "8080")
        base_url = f"http://localhost:{port}"
    return base_url


def _build_download_url(file_id: str, ctx=None) -> str:
    """Build a full download URL for the given file ID."""
    return f"{_get_base_url(ctx)}/download/{file_id}"


if TRANSPORT == "http":

    from mcp.server.fastmcp.server import Context as MCPContext

    @server.tool(
        name="create_upload_session",
        description=(
            "Creates an upload session and returns a full URL for uploading a file. "
            "POST the file to the returned `upload_url` using multipart form data with a `file` field. "
            "After upload, use the `uploaded_file_id` with the `convert_contents` tool. "
            "Use this to upload input files, reference documents, filters, or defaults files. "
            "The FILE-ID in the URL acts as the access key — no additional auth token is needed. "
            "Sessions expire after the configured TTL (default 7 days)."
        ),
    )
    async def create_upload_session(
        filename: Annotated[str, Field(description="Original filename (used to determine file extension)")] = "upload",
        ctx: MCPContext = None,
    ) -> dict:
        """Creates an upload session and returns the upload URL and file ID."""
        from .file_registry import registry as file_registry

        file_id = await file_registry.create_session(filename)
        base_url = _get_base_url(ctx)
        upload_url = f"{base_url}/upload/{file_id}"

        return {
            "upload_url": upload_url,
            "uploaded_file_id": file_id,
        }

    @server.tool(description=CONVERT_DESCRIPTION)
    async def convert_contents(
        contents: Annotated[str, Field(description="The content to be converted (required if uploaded_file_id not provided)")] = "",
        uploaded_file_id: Annotated[str, Field(description="File ID returned from create_upload_session. Use this to reference an uploaded input file.")] = "",
        input_format: Annotated[FORMATS, Field(description="Source format of the content")] = "markdown",
        output_format: Annotated[FORMATS, Field(description="Desired output format")] = "markdown",
        return_download_url: Annotated[bool, Field(description="When true, returns a full download URL for the converted file.")] = False,
        reference_doc_id: Annotated[str, Field(description="File ID of an uploaded reference document (for DOCX styling). Upload via create_upload_session first.")] = "",
        filter_ids: Annotated[list[str], Field(description="List of file IDs for uploaded Pandoc filter scripts. Upload each via create_upload_session first.")] = [],
        defaults_file_id: Annotated[str, Field(description="File ID of an uploaded Pandoc defaults YAML file. Upload via create_upload_session first.")] = "",
        ctx: MCPContext = None,
    ) -> str:
        """Converts content between different formats."""
        return await _do_convert(
            contents, "", uploaded_file_id, input_format, output_format, "",
            return_download_url, reference_doc_id, filter_ids, defaults_file_id,
            is_http=True, ctx=ctx,
        )

else:

    @server.tool(description=CONVERT_DESCRIPTION)
    async def convert_contents(
        contents: Annotated[str, Field(description="The content to be converted (required if input_file not provided)")] = "",
        input_file: Annotated[str, Field(description="Complete path to input file including filename and extension (e.g., '/path/to/input.md')")] = "",
        input_format: Annotated[FORMATS, Field(description="Source format of the content")] = "markdown",
        output_format: Annotated[FORMATS, Field(description="Desired output format")] = "markdown",
        output_file: Annotated[str, Field(description="Complete path where to save the output including filename and extension (required for pdf, docx, rst, latex, epub formats)")] = "",
        reference_doc: Annotated[str, Field(description="Path to a reference document to use for styling (supported for docx output format)")] = "",
        filters: Annotated[list[str], Field(description="List of Pandoc filter paths to apply during conversion. Filters are applied in the order specified.")] = [],
        defaults_file: Annotated[str, Field(description="Path to a Pandoc defaults file (YAML) containing conversion options. Similar to using pandoc -d option.")] = "",
    ) -> str:
        """Converts content between different formats."""
        return await _do_convert(
            contents, input_file, "", input_format, output_format, output_file,
            False, reference_doc, filters, defaults_file,
            is_http=False,
        )


async def _do_convert(
    contents: str,
    input_file: str,
    uploaded_file_id: str,
    input_format: FORMATS,
    output_format: FORMATS,
    output_file: str,
    return_download_url: bool,
    reference_doc_or_id: str,
    filters_or_ids: list[str],
    defaults_file_or_id: str,
    is_http: bool = False,
    ctx=None,
) -> str:
    """Core conversion logic shared by both transport modes."""
    print({
        "contents": contents[:50] + "..." if len(contents) > 50 else contents,
        "input_file": input_file,
        "uploaded_file_id": uploaded_file_id,
        "input_format": input_format,
        "output_format": output_format,
        "output_file": output_file,
        "return_download_url": return_download_url,
        "reference_doc_or_id": reference_doc_or_id,
        "filters_or_ids": filters_or_ids,
        "defaults_file_or_id": defaults_file_or_id,
    })

    if return_download_url and output_file:
        raise ValueError("return_download_url and output_file are mutually exclusive")

    from .file_registry import UPLOAD_DIR
    from .file_registry import registry as file_registry

    ext_map = {"markdown": ".md", "html": ".html", "pdf": ".pdf", "docx": ".docx", "rst": ".rst", "latex": ".tex", "epub": ".epub", "txt": ".txt", "ipynb": ".ipynb", "odt": ".odt"}

    effective_output_file = output_file
    if return_download_url:
        ext = ext_map.get(output_format, ".txt")
        effective_output_file = os.path.join(UPLOAD_DIR, f"output_{uuid.uuid4().hex}{ext}")

    resolved_input_file = None
    if uploaded_file_id:
        resolved_input_file = file_registry.resolve(uploaded_file_id)
        if resolved_input_file is None:
            raise ValueError(f"Uploaded file not found: {uploaded_file_id}")

    effective_input_file = resolved_input_file or input_file

    if not contents and not effective_input_file:
        raise ValueError("Either 'contents', 'input_file', or 'uploaded_file_id' must be provided")

    if is_http:
        reference_doc = file_registry.resolve(reference_doc_or_id) if reference_doc_or_id else None
        if reference_doc_or_id and not reference_doc:
            raise ValueError(f"Reference document not found: {reference_doc_or_id}")
        defaults_file = file_registry.resolve(defaults_file_or_id) if defaults_file_or_id else None
        if defaults_file_or_id and not defaults_file:
            raise ValueError(f"Defaults file not found: {defaults_file_or_id}")
        filters = []
        for fid in filters_or_ids:
            fpath = file_registry.resolve(fid)
            if not fpath:
                raise ValueError(f"Filter not found: {fid}")
            filters.append(fpath)
    else:
        reference_doc = reference_doc_or_id if reference_doc_or_id else None
        defaults_file = defaults_file_or_id if defaults_file_or_id else None
        filters = filters_or_ids

    if reference_doc:
        if output_format != "docx":
            raise ValueError("reference_doc is only supported for docx output format")
        if not os.path.exists(reference_doc):
            raise ValueError(f"Reference document not found: {reference_doc}")

    if defaults_file:
        if not os.path.exists(defaults_file):
            raise ValueError(f"Defaults file not found: {defaults_file}")
        try:
            with open(defaults_file) as f:
                yaml_content = yaml.safe_load(f)
            if not isinstance(yaml_content, dict):
                raise ValueError(f"Invalid defaults file format: {defaults_file} - must be a YAML dictionary")
            if 'to' in yaml_content and yaml_content['to'] != output_format:
                print(
                    f"Warning: Defaults file specifies output format '{yaml_content['to']}' "
                    f"but requested format is '{output_format}'. Using requested format."
                )
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing defaults file {defaults_file}: {str(e)}") from e
        except PermissionError as e:
            raise ValueError(f"Permission denied when reading defaults file: {defaults_file}") from e
        except Exception as e:
            raise ValueError(f"Error reading defaults file {defaults_file}: {str(e)}") from e

    supported_formats = {'html', 'markdown', 'pdf', 'docx', 'rst', 'latex', 'epub', 'txt', 'ipynb', 'odt'}
    if output_format not in supported_formats:
        raise ValueError(f"Unsupported output format: '{output_format}'. Supported formats are: {', '.join(supported_formats)}")

    advanced_formats = {'pdf', 'docx', 'rst', 'latex', 'epub'}
    if output_format in advanced_formats and not output_file and not return_download_url:
        raise ValueError(f"output_file path or return_download_url is required for {output_format} format")

    if filters:
        if not isinstance(filters, list):
            raise ValueError("filters parameter must be an array of strings")
        for filter_path in filters:
            if not isinstance(filter_path, str):
                raise ValueError("Each filter must be a string path")

    def resolve_filter_path(filter_path, defaults_file=None):
        if os.path.isabs(filter_path):
            paths = [filter_path]
        else:
            paths = [
                os.path.abspath(filter_path),
                os.path.join(os.path.dirname(os.path.abspath(defaults_file)), filter_path) if defaults_file else None,
                os.path.join(os.path.expanduser("~"), ".pandoc", "filters", os.path.basename(filter_path))
            ]
            paths = [p for p in paths if p]

        for path in paths:
            if os.path.exists(path):
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
        validated_filters = []
        for filter_path in filters:
            resolved_path = resolve_filter_path(filter_path, defaults_file)
            if resolved_path:
                validated_filters.append(resolved_path)
            else:
                raise ValueError(f"Filter not found in any of the searched locations: {filter_path}")
        return validated_filters

    def format_result_info(filters=None, defaults_file=None, validated_filters=None):
        filter_info = ""
        defaults_info = ""
        if filters and validated_filters:
            filter_names = [os.path.basename(f) for f in validated_filters]
            filter_info = f" with filters: {', '.join(filter_names)}"
        if defaults_file:
            defaults_info = f" using defaults file: {os.path.basename(defaults_file)}"
        return filter_info, defaults_info

    try:
        extra_args = []

        if defaults_file:
            defaults_file_abs = os.path.abspath(defaults_file)
            extra_args.extend(["--defaults", defaults_file_abs])

        env = os.environ.copy()
        output_dir = None
        if output_file:
            output_dir = os.path.dirname(os.path.abspath(output_file))
            env["PANDOC_OUTPUT_DIR"] = output_dir

        validated_filters = validate_filters(filters, defaults_file) if filters else []

        for filter_path in validated_filters:
            extra_args.extend(["--filter", filter_path])

        if output_format == "pdf":
            extra_args.extend([
                "--pdf-engine=xelatex",
                "-V", "geometry:margin=1in",
                "-V", "CJKmainfont=Noto Sans CJK SC",
                "-V", "CJKsansfont=Noto Sans CJK SC",
                "-V", "CJKmonofont=Noto Sans Mono CJK SC",
            ])

        if reference_doc and output_format == "docx":
            extra_args.extend(["--reference-doc", reference_doc])

        converted_output = None

        if effective_input_file:
            if not os.path.exists(effective_input_file):
                raise ValueError(f"Input file not found: {effective_input_file}")

            if effective_output_file:
                pypandoc.convert_file(
                    effective_input_file,
                    output_format,
                    outputfile=effective_output_file,
                    extra_args=extra_args
                )
                filter_info, defaults_info = format_result_info(filters, defaults_file, validated_filters)
                if return_download_url:
                    output_filename = f"output{ext_map.get(output_format, '.txt')}"
                    file_id = file_registry.register_output(effective_output_file, output_filename)
                    download_url = _build_download_url(file_id, ctx)
                    return f"File successfully converted{filter_info}{defaults_info}. Download: {download_url}"
                return f"File successfully converted{filter_info}{defaults_info} and saved to: {effective_output_file}"
            else:
                converted_output = pypandoc.convert_file(
                    effective_input_file,
                    output_format,
                    extra_args=extra_args
                )
        else:
            if effective_output_file:
                pypandoc.convert_text(
                    contents,
                    output_format,
                    format=input_format,
                    outputfile=effective_output_file,
                    extra_args=extra_args
                )
                filter_info, defaults_info = format_result_info(filters, defaults_file, validated_filters)
                if return_download_url:
                    output_filename = f"output{ext_map.get(output_format, '.txt')}"
                    file_id = file_registry.register_output(effective_output_file, output_filename)
                    download_url = _build_download_url(file_id, ctx)
                    return f"Content successfully converted{filter_info}{defaults_info}. Download: {download_url}"
                return f"Content successfully converted{filter_info}{defaults_info} and saved to: {effective_output_file}"
            else:
                converted_output = pypandoc.convert_text(
                    contents,
                    output_format,
                    format=input_format,
                    extra_args=extra_args
                )

        if not converted_output:
            raise ValueError("Conversion resulted in empty output")

        filter_info, defaults_info = format_result_info(filters, defaults_file, validated_filters)
        if filter_info:
            filter_info = f" (with filters: {', '.join([os.path.basename(f) for f in validated_filters])})"
        if defaults_info:
            defaults_info = f" (using defaults file: {os.path.basename(defaults_file)})"

        return (
            f'Following are the converted contents in {output_format} format{filter_info}{defaults_info}.\n'
            f'Ask user if they expect to save this file. If so, provide the output_file parameter with '
            f'complete path.\n'
            f'Converted Contents:\n\n{converted_output}'
        )

    except Exception as e:
        error_prefix = "Error converting"
        error_details = str(e)

        if "Filter not found" in error_details or "Filter is not executable" in error_details:
            error_prefix = "Filter error during conversion"
        elif "defaults" in error_details and defaults_file:
            error_prefix = "Defaults file error during conversion"
            error_details += f" (defaults file: {defaults_file})"
        elif "pandoc" in error_details.lower() and "not found" in error_details.lower():
            error_prefix = "Pandoc executable not found"
            error_details = "Please ensure Pandoc is installed and available in your PATH"

        raise ValueError(
            f"{error_prefix} {'file' if effective_input_file else 'contents'} from {input_format} to "
            f"{output_format}: {error_details}"
        ) from e
    finally:
        try:
            from .file_registry import registry as file_registry
            await file_registry.gc()
        except Exception:
            pass


async def main():
    """Run the mcp-pandoc server using stdin/stdout streams."""
    await server.run_stdio_async()
