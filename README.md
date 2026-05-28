[![Downloads](https://img.shields.io/pypi/dm/mcp-pandoc.svg)](https://pypi.python.org/pypi/mcp-pandoc)
[![CI](https://github.com/vivekVells/mcp-pandoc/actions/workflows/ci.yml/badge.svg)](https://github.com/vivekVells/mcp-pandoc/actions/workflows/ci.yml)
<br />

![image](https://github.com/user-attachments/assets/10f18317-58e7-430e-9aec-b706b60fe2c6)

<!-- [![Downloads](https://static.pepy.tech/badge/mcp-pandoc/month)](https://pepy.tech/project/mcp-pandoc) -->
<!-- ![PyPI - Downloads](https://img.shields.io/pypi/dm/mcp-pandoc?style=social) -->

<!--
[![Downloads](https://img.shields.io/pypi/dm/mcp-pandoc.svg)](https://pypi.python.org/pypi/mcp-pandoc)
[![CI](https://github.com/vivekVells/mcp-pandoc/actions/workflows/ci.yml/badge.svg)](https://github.com/vivekVells/mcp-pandoc/actions/workflows/ci.yml)
<a href="https://smithery.ai/server/mcp-pandoc"><img alt="Smithery Badge" src="https://smithery.ai/badge/mcp-pandoc"></a> <a href="https://glama.ai/mcp/servers/xyzzgaj9bk"><img width="380" height="200" src="https://glama.ai/mcp/servers/xyzzgaj9bk/badge" /></a> 
-->
[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/vivekvells-mcp-pandoc-badge.png)](https://mseep.ai/app/vivekvells-mcp-pandoc)
<a href="https://glama.ai/mcp/servers/xyzzgaj9bk"><img width="380" height="200" src="https://glama.ai/mcp/servers/xyzzgaj9bk/badge" />

# mcp-pandoc: A Document Conversion MCP Server

> Officially included in the [Model Context Protocol servers](https://github.com/modelcontextprotocol/servers/blob/main/README.md) open-source project. 🎉

## Overview

A Model Context Protocol server for document format conversion using [pandoc](https://pandoc.org/index.html). This server provides tools to transform content between different document formats while preserving formatting and structure.

Please note that mcp-pandoc is currently in early development. PDF support is under development, and the functionality and available tools are subject to change and expansion as we continue to improve the server.

Credit: This project uses the [Pandoc Python package](https://pypi.org/project/pandoc/) for document conversion, forming the foundation for this project.

## 📋 Quick Reference

**New to mcp-pandoc?** Check out **[📖 CHEATSHEET.md](CHEATSHEET.md)** for

- ⚡ Copy-paste examples for all formats
- 🔄 Bidirectional conversion matrix
- 🎯 Common workflows and pro tips
- 🌟 Reference document styling guide

_Perfect for quick lookups and getting started fast!_

## Demo

[![mcp-pandoc - v1: Seamless Document Format Conversion for Claude using MCP server](https://img.youtube.com/vi/vN3VOb0rygM/maxresdefault.jpg)](https://youtu.be/vN3VOb0rygM)

> 🎥 [Watch on YouTube](https://youtu.be/vN3VOb0rygM)

<details>
<summary>Screenshots</summary>

<img width="2407" alt="Screenshot 2024-12-26 at 3 33 54 PM" src="https://github.com/user-attachments/assets/ce3f5396-252a-4bba-84aa-65b2a06b859e" />
<img width="2052" alt="Screenshot 2024-12-26 at 3 38 24 PM" src="https://github.com/user-attachments/assets/8c525ad1-b184-41ca-b068-7dd34b60b85d" />
<img width="1498" alt="Screenshot 2024-12-26 at 3 40 51 PM" src="https://github.com/user-attachments/assets/a1e0682d-fe44-40b6-9988-bf805627beeb" />
<img width="760" alt="Screenshot 2024-12-26 at 3 41 20 PM" src="https://github.com/user-attachments/assets/1d7f5998-6d7f-48fa-adcf-fc37d0521213" />
<img width="1493" alt="Screenshot 2024-12-26 at 3 50 27 PM" src="https://github.com/user-attachments/assets/97992c5d-8efc-40af-a4c3-94c51c392534" />
</details>

More to come...

## Tools

The available tools depend on the transport mode:

### stdio Mode

1. **`convert_contents`** — Transforms content between supported formats
   - `contents` (string): Source content to convert (required if input_file not provided)
   - `input_file` (string): Complete path to input file (required if contents not provided)
   - `input_format` (string): Source format of the content (defaults to markdown)
   - `output_format` (string): Target format (defaults to markdown)
   - `output_file` (string): Complete path for output file (required for pdf, docx, rst, latex, epub formats)
   - `reference_doc` (string): Path to a reference document to use for styling (supported for docx output format)
   - `defaults_file` (string): Path to a Pandoc defaults file (YAML) containing conversion options
   - `filters` (array): List of Pandoc filter paths to apply during conversion
   - Supported input/output formats: markdown, html, pdf, docx, rst, latex, epub, txt, ipynb, odt
   - Note: For advanced formats (pdf, docx, rst, latex, epub), an output_file path is required

### HTTP Mode

1. **`create_upload_session`** — Creates an upload session and returns a full URL for uploading a file
   - `filename` (string): Original filename (used to determine file extension)
   - Returns: `{ "upload_url": "https://host/upload/FILE-ID", "uploaded_file_id": "FILE-ID" }`

2. **`convert_contents`** — Transforms content between supported formats
   - `contents` (string): Source content to convert (required if uploaded_file_id not provided)
   - `uploaded_file_id` (string): File ID returned from `create_upload_session`
   - `input_format` (string): Source format (defaults to markdown)
   - `output_format` (string): Target format (defaults to markdown)
   - `return_download_url` (boolean): When true, returns a full download URL for the converted file
   - `reference_doc_id` (string): File ID of an uploaded reference document (for DOCX styling)
   - `filter_ids` (array): List of file IDs for uploaded Pandoc filter scripts
   - `defaults_file_id` (string): File ID of an uploaded Pandoc defaults YAML file

### 🔧 Advanced Features

#### Defaults Files (YAML Configuration)

Use defaults files to create reusable conversion templates with consistent formatting:

```yaml
# academic-paper.yaml
from: markdown
to: pdf
number-sections: true
toc: true
metadata:
  title: "Academic Paper"
  author: "Research Team"
```

Example usage: `"Convert paper.md to PDF using defaults academic-paper.yaml and save as paper.pdf"`

#### Pandoc Filters

Apply custom filters for enhanced processing:

Example usage: `"Convert docs.md to HTML with filters ['/path/to/mermaid-filter.py'] and save as docs.html"`

> 💡 **For comprehensive examples and workflows**, see **[CHEATSHEET.md](CHEATSHEET.md)**

## 📊 Supported Formats & Conversions

### Bidirectional Conversion Matrix

| From\To      | MD  | HTML | TXT | DOCX | PDF | RST | LaTeX | EPUB | IPYNB | ODT |
| ------------ | --- | ---- | --- | ---- | --- | --- | ----- | ---- | ----- | --- |
| **Markdown** | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   | ✅    | ✅  |
| **HTML**     | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   | ✅    | ✅  |
| **TXT**      | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   | ✅    | ✅  |
| **DOCX**     | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   | ✅    | ✅  |
| **RST**      | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   | ✅    | ✅  |
| **LaTeX**    | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   | ✅    | ✅  |
| **EPUB**     | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   | ✅    | ✅  |
| **IPYNB**    | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   | ✅    | ✅  |
| **ODT**      | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   | ✅    | ✅  |

### A Note on PDF Support

This tool uses `pandoc` for conversions, which allows for generating PDF files from the formats listed above. However, converting _from_ a PDF to other formats is not supported. Therefore, PDF should be considered an **output-only** format.

### Format Categories

| Category     | Formats                     | Requirements                    |
| ------------ | --------------------------- | ------------------------------- |
| **Basic**    | MD, HTML, TXT, IPYNB, ODT   | None                            |
| **Advanced** | DOCX, PDF, RST, LaTeX, EPUB | Must specify `output_file` path |
| **Styled**   | DOCX with reference doc     | Custom template support ⭐      |

### Requirements by Format

- **PDF (.pdf)** - requires TeX Live installation (included in Docker image)
- **DOCX (.docx)** - supports custom styling via reference documents
- **All others** - no additional requirements

Note for stdio mode:

1. Complete file paths with filename and extension are required for advanced formats
2. **PDF conversion requires TeX Live installation** (see Critical Requirements section)
3. When no output path is specified:
   - Basic formats: Displays converted content in the chat
   - Advanced formats: May save in system temp directory (/tmp/ on Unix systems)

Note for HTTP mode:

1. Use `uploaded_file_id` for input files instead of local paths
2. Set `return_download_url=true` to get a download URL for the output
3. Upload reference documents, filters, and defaults files via `create_upload_session` first, then pass their file IDs

## Usage & configuration

**NOTE: Ensure to complete installing required packages mentioned below under "Critical Requirements".**

mcp-pandoc supports two transport modes: **stdio** (for local desktop use) and **HTTP** (for remote/container deployment).

### stdio Mode (Local Desktop Use)

For use with Claude Desktop or other MCP clients that connect via stdio:

```bash
{
  "mcpServers": {
    "mcp-pandoc": {
      "command": "uvx",
      "args": ["mcp-pandoc"]
    }
  }
}
```

In stdio mode, the `convert_contents` tool accepts local file paths (`input_file`, `output_file`) and path-based arguments for `reference_doc`, `filters`, and `defaults_file`.

### HTTP Mode (Remote Deployment)

For deployment as a containerized service (e.g., Aliyun Function Compute), set `MCP_PANDOC_TRANSPORT=http`:

```bash
{
  "mcpServers": {
    "mcp-pandoc": {
      "command": "uvx",
      "args": ["mcp-pandoc"],
      "env": {
        "MCP_PANDOC_TRANSPORT": "http",
        "MCP_PANDOC_AUTH_TOKEN": "your-secret-token",
        "MCP_PANDOC_PORT": "8080"
      }
    }
  }
}
```

In HTTP mode, the server exposes two tools and two REST endpoints:

#### MCP Tools (HTTP mode)

1. **`create_upload_session`** — Creates an upload session and returns a full upload URL
   - `filename` — Original filename (used to determine file extension)
   - Returns: `{ "upload_url": "https://host/upload/FILE-ID", "uploaded_file_id": "FILE-ID" }`

2. **`convert_contents`** — Converts content between formats
   - `contents` — Source content (required if `uploaded_file_id` not provided)
   - `uploaded_file_id` — File ID from `create_upload_session`
   - `input_format` — Source format (default: markdown)
   - `output_format` — Target format (default: markdown)
   - `return_download_url` — When true, returns a full download URL for the result
   - `reference_doc_id` — File ID of an uploaded reference document (for DOCX styling)
   - `filter_ids` — List of file IDs for uploaded Pandoc filter scripts
   - `defaults_file_id` — File ID of an uploaded Pandoc defaults YAML file

#### REST Endpoints (HTTP mode)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/upload/{file_id}` | POST | FILE-ID only | Upload file to a pre-created session |
| `/download/{file_id}` | GET | FILE-ID only | Download a file by its ID |
| `/mcp` | POST | Bearer token | MCP Streamable HTTP endpoint |

The FILE-ID in the URL path acts as the access key — no Bearer token is needed for upload/download. Unknown file IDs return 404.

#### HTTP Workflow Example

1. Call `create_upload_session(filename="report.md")` → returns upload URL and file ID
2. `POST` your file to the returned `upload_url` (multipart form, `file` field)
3. Call `convert_contents` with `uploaded_file_id` and `return_download_url=true`
4. `GET` the returned `download_url` to retrieve the converted file

**💡 Quick Start**: See **[CHEATSHEET.md](CHEATSHEET.md)** for copy-paste examples and common workflows.

### ⚠️ Important Notes

#### Critical Requirements

1. **Pandoc Installation** (stdio mode only)

- **Required**: Install `pandoc` — the core document conversion engine
- Installation:

  ```bash
  # macOS
  brew install pandoc

  # Ubuntu/Debian
  sudo apt-get install pandoc

  # Windows
  # Download installer from: https://pandoc.org/installing.html
  ```

- **Verify**: `pandoc --version`

2. **UV package installation** (stdio mode only)

- **Required**: Install `uv` package (includes `uvx` command)
- Installation:

  ```bash
  # macOS
  brew install uv

  # Windows/Linux
  pip install uv
  ```

- **Verify**: `uvx --version`

3. **PDF Conversion Prerequisites** (stdio mode only)

- TeX Live must be installed before attempting PDF conversion
- Installation commands:

  ```bash
  # Ubuntu/Debian
  sudo apt-get install texlive-xetex

  # macOS
  brew install texlive

  # Windows
  # Install MiKTeX or TeX Live from:
  # https://miktex.org/ or https://tug.org/texlive/
  ```

- **CJK Support**: For proper Chinese/Japanese/Korean character rendering in PDFs, also install:
  - Ubuntu/Debian: `sudo apt-get install texlive-lang-chinese fonts-noto-cjk`
  - macOS: `brew install font-noto-sans-cjk font-noto-serif-cjk`

> **Note**: HTTP mode (container deployment) includes all required dependencies in the Docker image — no local installation needed.

4. **File Path Requirements** (stdio mode only)

- When saving or converting files, you MUST provide complete file paths including filename and extension
- The tool does not automatically generate filenames or extensions
- **HTTP mode**: Use `uploaded_file_id` and `return_download_url` instead of file paths

#### Examples

✅ Correct Usage (stdio mode):

```bash
# Converting content to PDF
"Convert this text to PDF and save as /path/to/document.pdf"

# Converting between file formats
"Convert /path/to/input.md to PDF and save as /path/to/output.pdf"

# Converting to DOCX with a reference document template
"Convert input.md to DOCX using template.docx as reference and save as output.docx"

# Step-by-step reference document workflow
"First create a reference document: pandoc -o custom-reference.docx --print-default-data-file reference.docx" or if you already have one, use that
"Then convert with custom styling: Convert this text to DOCX using /path/to/custom-reference.docx as reference and save as /path/to/styled-output.docx"
```

✅ Correct Usage (HTTP mode):

```bash
# Step 1: Call create_upload_session with filename="report.md"
# → Returns: { "upload_url": "https://host/upload/abc123", "uploaded_file_id": "abc123" }

# Step 2: POST file to upload_url
curl -X POST "https://host/upload/abc123" -F "file=@report.md"

# Step 3: Convert with return_download_url=true
# → Returns: "File successfully converted. Download: https://host/download/def456"

# Step 4: Download the result
curl -o report.docx "https://host/download/def456"
```

❌ Incorrect Usage (stdio mode):

```bash
# Missing filename and extension
"Save this as PDF in /documents/"

# Missing complete path
"Convert this to PDF"

# Missing extension
"Save as /documents/story"
```

#### Common Issues and Solutions

1. **PDF Conversion Fails** (stdio mode)

   - Error: "xelatex not found"
   - Solution: Install TeX Live first (see installation commands above)

2. **File Conversion Fails** (stdio mode)

   - Error: "Invalid file path"
   - Solution: Provide complete path including filename and extension
   - Example: `/path/to/document.pdf` instead of just `/path/to/`

3. **Format Conversion Fails**

   - Error: "Unsupported format"
   - Solution: Use only supported formats:
     - Basic: txt, html, markdown
     - Advanced: pdf, docx, rst, latex, epub

4. **Reference Document Issues** (stdio mode)
   - Error: "Reference document not found"
   - Solution: Ensure the reference document path exists and is accessible
   - Note: Reference documents only work with DOCX output format
   - How to create: `pandoc -o reference.docx --print-default-data-file reference.docx`

5. **Upload/Download URL Shows localhost** (HTTP mode)
   - Issue: The returned upload/download URLs use `localhost` instead of the actual host
   - Solution: Ensure the `Host` header or `X-Forwarded-Host` header is correctly set by your reverse proxy/load balancer. The server extracts the base URL from the incoming request context.

6. **Upload Returns 404** (HTTP mode)
   - Issue: POST to `/upload/{file_id}` returns 404
   - Solution: You must first call `create_upload_session` to create a valid session. The FILE-ID in the URL must match a pending session.

## Quickstart

<!-- Uncomment after smithery fix
### Install

#### Option 1: Installing manually via claude_desktop_config.json config file
-->

### Installing manually via claude_desktop_config.json config file

- On MacOS: `open ~/Library/Application\ Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

a) Only for local development & contribution to this repo

<details>
  <summary>Development/Unpublished Servers Configuration</summary>

ℹ️ Replace <DIRECTORY> with your locally cloned project path

```bash
"mcpServers": {
  "mcp-pandoc": {
    "command": "uv",
    "args": [
      "--directory",
      "<DIRECTORY>/mcp-pandoc",
      "run",
      "mcp-pandoc"
    ]
  }
}
```

</details>

b) Published Servers Configuration - Consumers should use this config

```bash
"mcpServers": {
  "mcp-pandoc": {
    "command": "uvx",
    "args": [
      "mcp-pandoc"
    ]
  }
}
```

<!-- Uncomment after smithery cli fix
#### Option 2: To install Published Servers Configuration automatically via Smithery

Run the following bash command to install **published** [mcp-pandoc pypi](https://pypi.org/project/mcp-pandoc) for Claude Desktop automatically via [Smithery](https://smithery.ai/server/mcp-pandoc):

```bash
npx -y @smithery/cli install mcp-pandoc --client claude
```
-->

- If you face any issue, use the "Published Servers Configuration" above directly instead of this cli.

**Note**: To use locally configured mcp-pandoc, follow "Development/Unpublished Servers Configuration" step above.

## Development

### Testing

To run the comprehensive test suite:

```bash
uv run pytest tests/test_conversions.py       # Bidirectional format conversions
uv run pytest tests/test_http_transport.py    # HTTP mode integration tests
```

### Building and Publishing (PyPI)

To prepare the package for distribution:

1. Sync dependencies and update lockfile:

```bash
uv sync
```

2. Build package distributions:

```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:

```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:

- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Docker

Build the Docker image:

```bash
docker build -t mcp-pandoc:latest .
```

The Docker image includes:
- `pandoc` with `texlive-xetex` for PDF generation
- `texlive-lang-chinese` and `fonts-noto-cjk` for CJK character support
- All Python dependencies via `uv`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/vivekvells/Desktop/code/ai/mcp-pandoc run mcp-pandoc
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

---

## Contributing

We welcome contributions to enhance mcp-pandoc! Here's how you can get involved:

1. **Report Issues**: Found a bug or have a feature request? Open an issue on our [GitHub Issues](https://github.com/vivekVells/mcp-pandoc/issues) page.
2. **Submit Pull Requests**: Improve the codebase or add features by creating a pull request.

---
