# Local MCP Validation

Use this procedure to verify local branch changes through a dedicated Codex MCP server. It was created for the MCP SDK v2 migration and covers local registration, conversion through the changed server, output validation, error validation, and cleanup.

## Prerequisites

### 1. Prepare the local branch

Run from the repository root:

```bash
git branch --show-current
uv sync
pandoc --version
xelatex --version

VALIDATION_DIR="/tmp/mcp-pandoc-sdk2-validation-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$VALIDATION_DIR"
printf 'Validation directory: %s\n' "$VALIDATION_DIR"
```

### 2. Register the local MCP server

```bash
codex mcp add mcp-pandoc-sdk2-local -- \
  uv --directory "$(pwd)" run --locked mcp-pandoc

codex mcp get mcp-pandoc-sdk2-local --json
```

Restart Codex or open a new Codex terminal session from the repository root, then run:

```text
/mcp
```

Verify that `mcp-pandoc-sdk2-local` is connected and exposes `convert-contents`.

## Test paths

| Path | Conversion | Artifact validation | Error validation | After success |
|---|---|---|---|---|
| Manual | Send the conversion prompt | Run the shell checks | Send the invalid-input prompt | Remove MCP registration; preserve artifacts |
| Codex session | One prompt calls the MCP tool | The same prompt runs the shell checks | The same prompt tests invalid input | Remove MCP registration; preserve artifacts |

### Manual

Send this prompt in the new Codex session:

```text
Use only the mcp-pandoc-sdk2-local MCP server.

Call convert-contents separately for each conversion below. Use input_file
testing/input/test.md and input_format markdown for every call.
Replace <validation-directory> with the validation directory printed during
the prerequisite step.

1. output_format html, output_file <validation-directory>/output.html
2. output_format docx, output_file <validation-directory>/output.docx
3. output_format pdf, output_file <validation-directory>/output.pdf
4. output_format rst, output_file <validation-directory>/output.rst
5. output_format latex, output_file <validation-directory>/output.tex
6. output_format epub, output_file <validation-directory>/output.epub
7. output_format txt, output_file <validation-directory>/output.txt
8. output_format ipynb, output_file <validation-directory>/output.ipynb
9. output_format odt, output_file <validation-directory>/output.odt
10. output_format pptx, output_file <validation-directory>/output.pptx

Do not modify the source file. Report the result of every MCP call.
```

Validate the outputs:

```bash
for extension in html docx pdf rst tex epub txt ipynb odt pptx; do
  test -s "$VALIDATION_DIR/output.$extension"
done

file "$VALIDATION_DIR"/output.{html,docx,pdf,rst,tex,epub,txt,ipynb,odt,pptx}

rg -q "MCP-Pandoc Test Document" "$VALIDATION_DIR"/output.{html,rst,tex,txt,ipynb}

for extension in docx epub odt pptx; do
  pandoc "$VALIDATION_DIR/output.$extension" -t plain |
    rg -q "MCP-Pandoc Test Document"
done

file "$VALIDATION_DIR/output.pdf" | rg -q "PDF document"
```

Every command must exit successfully.

Validate MCP input errors:

```text
Use mcp-pandoc-sdk2-local to call convert-contents with contents "test" and
an unexpected parameter named unexpected set to true. Confirm that the tool
returns an input validation error and does not create a file.
```

Clean up:

```bash
codex mcp remove mcp-pandoc-sdk2-local
printf 'Artifacts preserved: %s\n' "$VALIDATION_DIR"
git status --short
```

Delete the artifacts only when they are no longer needed:

```bash
rm -rf "$VALIDATION_DIR"
```

Record the run using the result table in the Codex session prompt below.

### Codex session

Send this single prompt in the new Codex session:

```text
Validate the mcp-pandoc-sdk2-local MCP server.

1. In the terminal, resolve the repository root with git rev-parse
   --show-toplevel. Use <repository-root>/testing/input/test.md as the source,
   verify it exists and is non-empty, and create a unique validation directory
   named /tmp/mcp-pandoc-sdk2-validation-YYYYMMDD-HHMMSS using the current
   timestamp. Use that directory for every output. Do not modify the source.
2. Call convert-contents separately with input_format markdown and create:
   - HTML: <validation-directory>/output.html
   - DOCX: <validation-directory>/output.docx
   - PDF: <validation-directory>/output.pdf
   - RST: <validation-directory>/output.rst
   - LaTeX: <validation-directory>/output.tex
   - EPUB: <validation-directory>/output.epub
   - TXT: <validation-directory>/output.txt
   - IPYNB: <validation-directory>/output.ipynb
   - ODT: <validation-directory>/output.odt
   - PPTX: <validation-directory>/output.pptx
3. Verify every output exists and is non-empty.
4. Verify the HTML, RST, LaTeX, TXT, and IPYNB outputs contain
   "MCP-Pandoc Test Document".
5. Convert the DOCX, EPUB, and ODT outputs back to plain text with Pandoc and
   verify each contains "MCP-Pandoc Test Document".
6. Verify that file identifies output.pdf as a PDF document.
7. Call convert-contents with contents "test" and an unexpected parameter
   named unexpected set to true. Verify it returns an input validation error.
8. If every check passes, remove the mcp-pandoc-sdk2-local MCP registration,
   preserve the validation directory, report its exact path, and show
   git status --short.
9. Always finish with a Markdown result table containing these rows: MCP
   connection and tool discovery, HTML, DOCX, PDF, RST, LaTeX, EPUB, TXT,
   IPYNB, ODT, invalid-input rejection, MCP registration cleanup, and artifact
   preservation. Use only PASS, FIXED, FAIL, NOT RUN, or SKIPPED as statuses.
   Include concise evidence for every row, the overall result, and the exact
   validation directory.

Stop on the first failure, report it, and preserve the MCP registration and
temporary files for diagnosis. Still produce the result table and mark all
subsequent checks NOT RUN.

Always use this final output format:

Overall: <PASS or FAIL>
Validation directory: <absolute path>

| Check | Status | Evidence |
|---|---|---|
| MCP connection and tool discovery | | |
| HTML | | |
| DOCX | | |
| PDF | | |
| RST | | |
| LaTeX | | |
| EPUB | | |
| TXT | | |
| IPYNB | | |
| ODT | | |
| Invalid-input rejection | | |
| MCP registration cleanup | | |
| Artifact preservation | | |

Status meanings:

- PASS: check succeeded.
- FIXED: a previously failing check succeeded after a change.
- FAIL: check failed in this run.
- NOT RUN: execution stopped before this check.
- SKIPPED: check was intentionally omitted with a stated reason.
```
