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

| From\To      | MD  | HTML | TXT | DOCX | PDF | RST | LaTeX | EPUB |
| ------------ | --- | ---- | --- | ---- | --- | --- | ----- | ---- |
| **Markdown** | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   |
| **HTML**     | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   |
| **TXT**      | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   |
| **DOCX**     | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   |
| **PDF**      | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   |
| **RST**      | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   |
| **LaTeX**    | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   |
| **EPUB**     | ✅  | ✅   | ✅  | ✅   | ✅  | ✅  | ✅    | ✅   |

### Format Categories

| Category     | Formats                     | Requirements                    |
| ------------ | --------------------------- | ------------------------------- |
| **Basic**    | MD, HTML, TXT               | None                            |
| **Advanced** | DOCX, PDF, RST, LaTeX, EPUB | Must specify `output_file` path |
| **Styled**   | DOCX with reference doc     | Custom template support ⭐      |

## ⚡ Quick Examples

### Content-to-Format Conversions

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
```

### Reference Document Styling (⭐ NEW Feature)

```bash
# Step 1: Create reference document
pandoc -o /tmp/reference.docx --print-default-data-file reference.docx

# Step 2: Use reference for styled conversion
"Convert this to DOCX using /tmp/reference.docx as reference and save as /tmp/styled.docx:
# Professional Report
This will be styled according to the reference document."
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

## 💡 Pro Tips

### File Paths

| ✅ Correct               | ❌ Incorrect           |
| ------------------------ | ---------------------- |
| `/tmp/document.pdf`      | `/tmp/document`        |
| `C:\Documents\file.docx` | `C:\Documents\`        |
| `./output/report.html`   | `just convert to HTML` |

### Format-Specific Notes

| Format    | Requirements           | Notes                   |
| --------- | ---------------------- | ----------------------- |
| **PDF**   | TeX Live installed     | Uses XeLaTeX engine     |
| **DOCX**  | Optional reference doc | Supports custom styling |
| **EPUB**  | Output file required   | Good for e-books        |
| **LaTeX** | Output file required   | Academic documents      |

### Reference Documents

| Use Case               | Command                                                       |
| ---------------------- | ------------------------------------------------------------- |
| **Create default**     | `pandoc -o ref.docx --print-default-data-file reference.docx` |
| **Corporate branding** | Customize ref.docx in Word/LibreOffice → Save                 |
| **Apply styling**      | Add `reference_doc: "/path/to/ref.docx"` parameter            |

### Error Troubleshooting

| Error                                   | Solution                                    |
| --------------------------------------- | ------------------------------------------- |
| "xelatex not found"                     | Install TeX Live                            |
| "Reference document not found"          | Check file path exists                      |
| "output_file path is required"          | Add complete file path for advanced formats |
| "only supported for docx output format" | Reference docs only work with DOCX          |

## 🎯 Parameter Quick Reference

| Parameter       | Type   | Required | Description                   | Example                     |
| --------------- | ------ | -------- | ----------------------------- | --------------------------- |
| `contents`      | string | ✅\*     | Text to convert               | `"# Hello World"`           |
| `input_file`    | string | ✅\*     | File to convert               | `"/path/input.md"`          |
| `output_format` | string | ✅       | Target format                 | `"docx"`, `"pdf"`, `"html"` |
| `output_file`   | string | ⚠️\*\*   | Save location                 | `"/path/output.docx"`       |
| `input_format`  | string | ❌       | Source format (auto-detected) | `"markdown"`                |
| `reference_doc` | string | ❌       | DOCX template                 | `"/path/template.docx"`     |

\*Either `contents` OR `input_file` required  
\*\*Required for: PDF, DOCX, RST, LaTeX, EPUB

---

_This cheatsheet covers mcp-pandoc v0.3.4+ with reference document support_
