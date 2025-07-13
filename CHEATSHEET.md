# mcp-pandoc Quick Reference Cheatsheet

_Last Updated: June 27, 2025_

## 🚀 Prerequisites (One-Time Setup)

| Component               | macOS                  | Ubuntu/Debian                        | Windows                                                               |
| ----------------------- | ---------------------- | ------------------------------------ | --------------------------------------------------------------------- |
| **Pandoc**              | `brew install pandoc`  | `sudo apt-get install pandoc`        | [Download installer](https://pandoc.org/installing.html)              |
| **UV**                  | `brew install uv`      | `pip install uv`                     | `pip install uv`                                                      |
| **TeX Live** (PDF only) | `brew install texlive` | `sudo apt-get install texlive-xetex` | [MiKTeX](https://miktex.org/) or [TeX Live](https://tug.org/texlive/) |

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
| **Styled**   | DOCX with reference doc     | Custom template support         |

## ⚡ Quick Examples

### Simple Text-to-Format Conversions

```bash
# Markdown to HTML (displayed)
"Convert this to HTML: # Hello World"

# Markdown to DOCX (saved)
"Convert this to DOCX and save as /tmp/doc.docx: # My Document"

# Markdown to PDF (saved)
"Convert this to PDF and save as /tmp/doc.pdf: # My Document"
```

### File-to-File Conversions

```bash
# DOCX to PDF
"Convert /path/input.docx to PDF and save as /path/output.pdf"

# Markdown to DOCX
"Convert /path/input.md to DOCX and save as /path/output.docx"

# HTML to Markdown
"Convert /path/input.html to Markdown and save as /path/output.md"

# IPYNB to HTML
"Convert /path/input.ipynb to HTML and save as /path/output.html"

# ODT to Markdown
"Convert /path/input.odt to Markdown and save as /path/output.md"
```

### Reference Document Styling

```bash
# Step 1: Create reference document
pandoc -o /tmp/reference.docx --print-default-data-file reference.docx

# Step 2: Use reference for styled conversion
"Convert this to DOCX using /tmp/reference.docx as reference and save as /tmp/styled.docx:
# Professional Report
This will be styled according to the reference document."
```

### Consistent Configuration with Defaults Files

```bash
# Create a defaults file for academic papers
"Create defaults file /tmp/academic.yaml with: 
from: markdown
to: pdf
number-sections: true
toc: true
bibliography: references.bib"

# Use defaults for conversion
"Convert paper.md to PDF using defaults /tmp/academic.yaml and save as paper.pdf"

# Web publishing defaults
"Convert blog.md to HTML using defaults /tmp/web.yaml and save as blog.html"
```

### Enhanced Processing with Filters

```bash
# Single filter for Mermaid diagrams
"Convert docs.md to HTML with filters ['/path/to/mermaid-filter.py'] and save as docs.html"

# Multiple filters for academic workflow
"Convert thesis.md to PDF with filters ['/filters/citations.py', '/filters/crossref.py'] and save as thesis.pdf"

# Combine defaults and filters
"Convert paper.md to HTML using defaults /tmp/academic.yaml with filters ['/filters/mermaid.py'] and save as paper.html"
```

## 🔄 Common Workflows

### Publishing Pipeline

| Step | Command                                                  | Output            |
| ---- | -------------------------------------------------------- | ----------------- |
| 1    | `"Convert manuscript.md to DOCX and save as draft.docx"` | Draft for review  |
| 2    | `"Convert draft.docx to PDF and save as final.pdf"`      | Publication ready |

### Documentation Workflow

| Step | Command                                                   | Purpose           |
| ---- | --------------------------------------------------------- | ----------------- |
| 1    | `"Convert README.md to HTML and save as docs/index.html"` | Web documentation |
| 2    | `"Convert README.md to PDF and save as docs/manual.pdf"`  | Printable manual  |

### Professional Reports

| Step | Command                                                                                | Result             |
| ---- | -------------------------------------------------------------------------------------- | ------------------ |
| 1    | Create template: `pandoc -o template.docx --print-default-data-file reference.docx`    | Custom styling     |
| 2    | `"Convert report.md to DOCX using template.docx as reference and save as report.docx"` | Branded document   |
| 3    | `"Convert report.docx to PDF and save as report.pdf"`                                  | Final distribution |

### Academic Documents with Filters

| Step | Command                                                                                         | Purpose               |
| ---- | ----------------------------------------------------------------------------------------------- | --------------------- |
| 1    | Create filter: `echo '#!/usr/bin/env python3' > /tmp/citation_filter.py`                       | Custom citations      |
| 2    | `"Convert paper.md to PDF with filters ['/tmp/citation_filter.py'] and save as paper.pdf"`     | Processed citations   |
| 3    | `"Convert paper.md to DOCX with filters ['/tmp/mermaid_filter.py'] and save as paper.docx"`    | Diagram processing    |

### Streamlined Workflow with Defaults Files

| Step | Command                                                                                    | Benefit              |
| ---- | ------------------------------------------------------------------------------------------ | -------------------- |
| 1    | Create defaults: `echo 'to: html\nstandalone: true\ncss: [style.css]' > /tmp/web.yaml`    | Reusable config      |
| 2    | `"Convert docs.md to HTML using defaults /tmp/web.yaml and save as docs.html"`            | Consistent styling   |
| 3    | `"Convert blog.md to HTML using defaults /tmp/web.yaml and save as blog.html"`            | Same config applied  |

## 💡 Pro Tips

### File Paths

| ✅ Correct               | ❌ Incorrect           |
| ------------------------ | ---------------------- |
| `/tmp/document.pdf`      | `/tmp/document`        |
| `C:\Documents\file.docx` | `C:\Documents\`        |
| `./output/report.html`   | `just convert to HTML` |

### Format-Specific Notes

| Format         | Requirements           | Notes                     |
| -------------- | ---------------------- | ------------------------- |
| **PDF**        | TeX Live installed     | Uses XeLaTeX engine       |
| **DOCX**       | Optional reference doc | Supports custom styling   |
| **EPUB**       | Output file required   | Good for e-books          |
| **LaTeX**      | Output file required   | Academic documents        |
| **Defaults**   | YAML format           | Reusable configurations   |
| **Filters**    | Executable scripts    | Custom content processing |

### Reference Documents

| Use Case               | Command                                                       |
| ---------------------- | ------------------------------------------------------------- |
| **Create default**     | `pandoc -o ref.docx --print-default-data-file reference.docx` |
| **Corporate branding** | Customize ref.docx in Word/LibreOffice → Save                 |
| **Apply styling**      | Add `reference_doc: "/path/to/ref.docx"` parameter            |

### Defaults Files

| Use Case                  | Example YAML Content                                          |
| ------------------------- | ------------------------------------------------------------- |
| **Academic paper**        | `from: markdown\nto: pdf\nnumber-sections: true\ntoc: true`  |
| **Web publishing**        | `to: html\nstandalone: true\ncss: [style.css]\nself-contained: true` |
| **E-book creation**       | `to: epub\nmetadata:\n  title: "My Book"\n  author: "Author Name"` |

### Pandoc Filters

| Filter Type           | Purpose                      | Example Usage                               |
| --------------------- | ---------------------------- | ------------------------------------------- |
| **Mermaid diagrams**  | Convert code blocks to SVG   | `filters: ['/path/to/mermaid-filter.py']`   |
| **Citation processing** | Format academic citations   | `filters: ['/path/to/pandoc-citeproc']`     |
| **Custom formatting** | Transform specific elements  | `filters: ['/filters/custom.py']`           |

### Error Troubleshooting

| Error                                   | Solution                                    |
| --------------------------------------- | ------------------------------------------- |
| "xelatex not found"                     | Install TeX Live                            |
| "Reference document not found"          | Check file path exists                      |
| "output_file path is required"          | Add complete file path for advanced formats |
| "only supported for docx output format" | Reference docs only work with DOCX          |
| "Defaults file not found"              | Verify YAML file path and accessibility     |
| "Filter not executable"                | Check filter permissions: `chmod +x filter.py` |
| "Invalid YAML in defaults file"        | Validate YAML syntax and structure          |

## 🎯 Parameter Quick Reference

| Parameter       | Type   | Required | Description                   | Example                     |
| --------------- | ------ | -------- | ----------------------------- | --------------------------- |
| `contents`      | string | ✅\*     | Text to convert               | `"# Hello World"`           |
| `input_file`    | string | ✅\*     | File to convert               | `"/path/input.md"`          |
| `output_format` | string | ✅       | Target format                 | `"docx"`, `"pdf"`, `"html"` |
| `output_file`   | string | ⚠️\*\*   | Save location                 | `"/path/output.docx"`       |
| `input_format`  | string | ❌       | Source format (auto-detected) | `"markdown"`                |
| `reference_doc` | string | ❌       | DOCX template                 | `"/path/template.docx"`     |
| `defaults_file` | string | ❌       | Pandoc defaults YAML config   | `"/path/defaults.yaml"`     |
| `filters`       | array  | ❌       | Pandoc filters list           | `["/path/filter.py"]`       |

\*Either `contents` OR `input_file` required  
\*\*Required for: PDF, DOCX, RST, LaTeX, EPUB

---

_Quick reference for mcp-pandoc document conversion capabilities_
