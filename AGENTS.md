# AGENTS.md

Map of this repo. Start here, then navigate to the source of truth you need.

Keep this file thin. It is loaded into context on every task, so it points at detail rather than containing it. If you are adding rules, they belong in the linked docs, not here.

`CLAUDE.md` is the standards document behind every review here: semantic versioning policy, the documentation checklist, test organisation, and the PR review framework. Claude Code loads it automatically. **If you are any other agent, read it explicitly.** You will be held to it either way.

---

## What this is

`mcp-pandoc` is an MCP server exposing document format conversion via pandoc. One tool, `convert-contents`, eight parameters, stdio transport.

- Published: [PyPI `mcp-pandoc`](https://pypi.org/project/mcp-pandoc/) · run with `uvx mcp-pandoc`
- Public repo with external contributors. Treat the tool name, parameters, schema, and error semantics as a **public API**.

---

## Where things are

| Need | Go to |
|---|---|
| The whole server | [`src/mcp_pandoc/server.py`](src/mcp_pandoc/server.py) |
| Tool definition and schema | `server.py` → `handle_list_tools()` |
| Conversion + validation | `server.py` → `handle_call_tool()` |
| SDK v2 adapters | `server.py` → `list_tools()`, `call_tool()` |
| Entry point | [`src/mcp_pandoc/__init__.py`](src/mcp_pandoc/__init__.py) |
| Format matrix tests | [`tests/test_conversions.py`](tests/test_conversions.py) |
| Filters, defaults files | [`tests/test_advanced_features.py`](tests/test_advanced_features.py) |
| Startup + handshake regression | [`tests/test_server_startup.py`](tests/test_server_startup.py) |
| CI | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| Dependencies and version | [`pyproject.toml`](pyproject.toml) |

## Deeper context

| Topic | Doc |
|---|---|
| Project philosophy, PR review framework, maintenance standards | [`CLAUDE.md`](CLAUDE.md) |
| How to contribute, tiered by change size | [`CONTRIBUTING.md`](CONTRIBUTING.md) · read this before opening a PR |
| User-facing docs | [`README.md`](README.md) · [`CHEATSHEET.md`](CHEATSHEET.md) |
| Local MCP validation steps | [`MCP_LOCAL_VALIDATION.md`](MCP_LOCAL_VALIDATION.md) |
| Audits: verified findings behind open work | [`docs/audits/`](docs/audits/) |

---

## Commands

```bash
uv sync                                   # install
uv run mcp-pandoc                         # run the server (stdio, will block)
uv run pytest                             # all tests
uv run pytest tests/test_server_startup.py  # handshake regression
uv run ruff check .                       # lint
uv build                                  # package
```

Requires system `pandoc`. PDF output additionally requires a TeX engine (`xelatex`).

---

## Non-negotiables

- **Never commit directly to `main`.** Branch, PR, wait for approval. Full workflow in [`CLAUDE.md`](CLAUDE.md).
- **The tool contract is public API.** The tool name, the eight parameter names, the schema, and the `isError` error semantics. Changing any of them is a breaking change even when no schema field visibly moves.
- **Return `isError` with an actionable sentence. Do not raise.** The consumer is a language model; it reads that text and self-corrects. A raised exception becomes "the tool failed" and it cannot.
- **Never `print()` in `src/`.** stdout carries the JSON-RPC protocol. Use MCP logging notifications.
- **Only enumerate formats verified in the direction being enumerated.** Pandoc reads and writes different sets. See [`docs/audits/`](docs/audits/).
- **Cap the SDK major version.** An uncapped `mcp` dependency broke every fresh install for eleven months. See [#40](https://github.com/vivekVells/mcp-pandoc/issues/40).

---

## Issue conventions

- Work is tracked in GitHub issues, not in files.
- Every issue opens with a **Links** block: source discussion, evidence doc, code path.
- Issues state the problem and acceptance criteria. **They do not prescribe the implementation.** Decide that when picking the issue up.
- Findings that need long-form evidence go in [`docs/audits/`](docs/audits/), and the issue links to the relevant section rather than restating it.
