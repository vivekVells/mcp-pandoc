# Contributing to mcp-pandoc

Thank you for your interest in contributing! Choose your path below:

Start with [`AGENTS.md`](AGENTS.md) for the map of the repo and the non-negotiables. [`CLAUDE.md`](CLAUDE.md) holds the standards every PR is reviewed against: semantic versioning policy, the documentation checklist, and test organisation.

## 🚀 Quick Start (Simple Changes)

**Fixing docs, typos, or small bugs?**

1. **Fork & clone:** `git clone your-fork-url`
2. **Make your change:** Edit the files you need
3. **Test:** `uv run pytest tests/test_conversions.py`
4. **Submit PR:** Include screenshots showing it works

That's it! The PR template will guide you through the rest.

**Need to add features or understand the codebase?** Expand the sections below.

---

<details>
<summary>📦 Full Development Setup (expand for new features)</summary>

## Prerequisites

### Required Dependencies
```bash
# Core dependencies (required for all development)
# macOS
brew install pandoc uv

# Ubuntu/Debian
sudo apt-get install pandoc
pip install uv

# Windows
# Download pandoc from: https://pandoc.org/installing.html
pip install uv
```

### Optional: PDF Support
If working with PDF conversion features:

```bash
# macOS
brew install texlive

# Ubuntu/Debian
sudo apt-get install texlive-xetex

# Windows
# Install MiKTeX or TeX Live from:
# https://miktex.org/ or https://tug.org/texlive/
```

## Development Setup

1. **Clone and setup:**
   ```bash
   git clone https://github.com/vivekVells/mcp-pandoc.git
   cd mcp-pandoc
   uv sync
   ```

2. **Test everything works:**
   ```bash
   uv run pytest tests/test_conversions.py
   uv run mcp-pandoc
   ```

</details>

<details>
<summary>🏗️ Understanding the Codebase (expand to learn architecture)</summary>

## Project Structure

```
/mcp-pandoc/
├── src/mcp_pandoc/
│   ├── __init__.py              # Entry point
│   └── server.py                # Main MCP server implementation
├── tests/
│   ├── fixtures/                # Test input files for all formats
│   ├── output/                  # Test output directory
│   └── test_conversions.py      # Comprehensive format testing
├── README.md                    # User documentation
├── CHEATSHEET.md               # Quick reference guide
└── pyproject.toml              # Python project configuration
```

## Core Architecture
- **MCP Server**: Implements Model Context Protocol for document conversion
- **Primary Tool**: `convert-contents` handles all format conversions
- **Supported Formats**: 9 read and write, plus pdf and pptx which are write only
- **Format Categories**:
  - **Basic**: md, html, txt, ipynb (converted content is returned inline)
  - **Advanced**: pdf, docx, odt, pptx, rst, latex, epub (require output file paths)

## Key Files
- `src/mcp_pandoc/server.py`: Core server implementation with tool definitions
- `tests/test_conversions.py`: Parametrized testing for all format combinations
- `pyproject.toml`: Dependencies and build configuration

</details>

<details>
<summary>⚙️ Development Guidelines (expand for code standards)</summary>

## Code Quality Standards

### Linting (Required)
**Run all three before pushing. CI runs all three and will fail if any of them does.**

```bash
# Python code quality (catches syntax errors like false vs False)
uv run ruff check .

# YAML file validation (CI configs, etc.)
uv run yamllint .

# Trailing whitespace, missing final newlines, YAML/JSON validity
uv run pre-commit run --all-files
```

`ruff` is configured to skip `tests/*`, so test files are covered only by `pre-commit`. If you added or edited a test, run it.

**When to run:**
- **Before committing**: `pre-commit install` once, and the hooks run on every commit
- **After changes**: Verify your code meets standards
- **CI will fail** if any of the three doesn't pass

**What it catches:**
- Syntax errors that broke production (PR #31: `false` vs `False`)
- Code style inconsistencies
- YAML formatting issues in configs

### Code Standards

1. **Follow Existing Patterns**:
   - Study `src/mcp_pandoc/server.py` for coding style
   - Use async/await patterns for MCP operations
   - Implement comprehensive error handling

2. **Type Hints**: All functions should include proper type annotations

3. **Error Handling**: Provide clear, actionable error messages
   ```python
   # Good
   raise ValueError(f"Output file path is required for {output_format} format")

   # Bad
   raise ValueError("Invalid format")
   ```

4. **JSON Schema Validation**: New parameters must include proper schema definitions

## Testing Requirements

CI runs the full test suite on Ubuntu and Windows with Python 3.11 and 3.13.
The `CI OK` check passes only when lint and every test-matrix job succeeds.

1. **Run Tests**: Always run the full test suite before submitting changes
   ```bash
   uv run pytest
   ```

2. **Add Tests**: New functionality must include corresponding tests

3. **Test Coverage**: The project uses parametrized testing to verify all format combinations work correctly

4. **Manual Testing**: Test with MCP Inspector if making server changes:
   ```bash
   npx @modelcontextprotocol/inspector uv --directory $(pwd) run mcp-pandoc
   ```

## Documentation Requirements

1. **Update README.md**: Document new features with clear examples
2. **Update CHEATSHEET.md**: Add quick reference examples for new functionality
3. **Update Tool Descriptions**: Modify docstrings in `server.py` for parameter changes
4. **Version Documentation**: Note any breaking changes or new requirements

</details>

<details>
<summary>🔄 Format Support (expand if adding new formats)</summary>

## Current Support Matrix
- **Read and write**: md, html, txt, docx, odt, rst, latex, epub, ipynb
- **Write only**: pdf (pandoc has no PDF reader in any release) and pptx (the pandoc pptx reader arrived in 3.8.3, which most distro packages do not ship yet; see [#54](https://github.com/vivekVells/mcp-pandoc/issues/54))
- **Require an `output_file`**: pdf, docx, odt, pptx, rst, latex, epub
- **Reference document styling**: docx, odt, pptx, with the reference matching the output format

## Adding New Formats
1. Update the `supported_formats` set in `handle_call_tool` (`server.py`)
2. Add the format to the `input_format` and/or `output_format` enum in `handle_list_tools`, but **only to the direction you have verified**
3. Add to `advanced_formats` if the format is binary and needs an `output_file`
4. Create test fixtures in `tests/fixtures/`
5. Update documentation and the conversion matrix in README.md and CHEATSHEET.md
6. Test the conversions you claim, in the direction you claim them

## Only document what the schema exposes

Pandoc reads and writes different sets of formats, and the version a user has installed changes what is available. Before writing a format into README.md, CHEATSHEET.md, or the tool description, check that it is present in the matching enum in `server.py`, and that you verified it in the direction you are claiming.

The tool description and JSON schema are read by a language model before it decides what to call. A description promising a format the enum rejects makes the model attempt it, fail, and retry.

</details>

## Versioning

Feature commits carry their own version bump. New backwards-compatible feature = MINOR, bug fix = PATCH.

Three places carry the version. Two declare it, one asserts it, and they must move together:

| File | What to change |
|---|---|
| `pyproject.toml` | `version = "..."` |
| `src/mcp_pandoc/server.py` | `Server("mcp-pandoc", version="...")` |
| `tests/test_server_startup.py` | the version literal in the handshake assertion |

Then run `uv sync` so `uv.lock` matches. `tests/test_advanced_features.py` asserts `pyproject.toml` and `server.py` agree, and the startup test asserts the version a client sees. Updating only one will fail.

## Reporting your environment

What pandoc can do depends on the **pandoc binary you have installed**, which this project does not pin. A passing test is evidence about your machine, not about pandoc. Include in your PR:

- `pandoc --version` (first line)
- Operating system and version
- Python version

State the version alongside any capability claim. Write "pandoc 3.7.0.2 accepts `--reference-doc` for odt", not "pandoc accepts `--reference-doc` for odt".

## AI-assisted contributions

Assistants are welcome here, and [`AGENTS.md`](AGENTS.md) is written for them. If you are one:

1. **Navigate with [`AGENTS.md`](AGENTS.md).** It maps the repo and lists what must never change.
2. **Read [`CHEATSHEET.md`](CHEATSHEET.md)** to learn what the server actually supports before proposing anything. Do not infer capability from the code alone.
3. **Add or update tests for the user scenario you changed**, not for coverage. One test that proves the feature does its job beats five that prove a file was created.
4. **Update [`CHEATSHEET.md`](CHEATSHEET.md) and README.md** if user-visible behaviour changed, including new error messages a user might hit.
5. **Give reviewers what they need**: the environment block above, the real command output rather than a summary of it, and an explicit note on anything you could not verify.
6. **Keep the diff to the issue.** If you find an adjacent problem, say so in the PR and open an issue rather than widening the branch.

You are accountable for the diff regardless of how it was produced. A human should run the checks before you push.

## Getting Help

- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions about usage or development
- **Testing**: Use MCP Inspector for debugging server interactions

## Code of Conduct

This project follows standard open source community guidelines:
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Maintain a professional and welcoming environment

---

Thank you for contributing to mcp-pandoc! Your efforts help make document conversion more accessible for everyone.
