# Audit: agent workflow gaps, August 2026

Evidence behind the issues opened after [#40](https://github.com/vivekVells/mcp-pandoc/issues/40). Issues link here rather than restating findings.

| | |
|---|---|
| **Prompted by** | [@pbarone's workflow description](https://github.com/vivekVells/mcp-pandoc/issues/40#issuecomment-5182935810) |
| **Audited** | mcp-pandoc v0.9.0 (`ef3de10`) |
| **Verified against** | pandoc 3.7.0.2, mcp python SDK 2.x, macOS |
| **Date** | 2026-08-08 |

Every finding below was reproduced by running the command shown. None are recalled or inferred.

---

## The workflow being audited

A user described the pipeline he runs mcp-pandoc inside of. Auditing against a real workflow rather than against the feature list is what surfaced these.

```
        markdown in git = single source of truth
             │
  OUTBOUND   │  md ──reference_doc=house.docx──► .docx ──► review ──► distribute
             │       Word files are disposable builds, never edited by hand
             │
  INBOUND    │  inbound .docx ──► md ──┐
             │  inbound .pptx ──► md ──┴──► agent reads and reasons over them
```

It runs as an MCP server rather than CLI calls because conversion is one step inside an agent loop: the agent researches, edits the markdown, builds the Word file, and publishes, without the human switching tools.

---

## Finding 1: pandoc cannot read PDF, but the schema offers it

`input_format` includes `pdf` at [`server.py:114`](../../src/mcp_pandoc/server.py#L114).

```console
$ pandoc -f pdf b.pdf -t markdown
Unknown input format pdf
Pandoc can convert to PDF, but not from PDF.

$ pandoc --list-input-formats | grep -c pdf
0
```

**Impact.** The input schema is a promise made to a language model. A model reading `pdf` in the enum will attempt PDF input confidently, fail, and often retry the same impossible call. A human reading CLI `--help` would simply try something else.

Tracked in the `pdf` input enum issue.

---

## Finding 2: pandoc cannot read pptx, and can write it

```console
$ pandoc --list-output-formats | grep -w pptx
pptx

$ pandoc -f pptx deck.pptx -t markdown
Unknown input format pptx
```

**Impact.** The user's inbound `.pptx → markdown` step cannot work with pandoc, and nothing in the schema or docs says so. Separately, pptx **output** is a pandoc capability the server does not expose.

Implementing a pptx reader would require `python-pptx`, a non-pandoc dependency, which is a red-light item under the project philosophy in [`CLAUDE.md`](../../CLAUDE.md).

Tracked in the pptx output-only issue.

---

## Finding 3: read and write format support are not symmetric

The same ten-value enum backs both `input_format` and `output_format`, which tells the model that anything readable is writable and vice versa.

```
              READ    WRITE
   markdown    yes     yes
   html        yes     yes
   docx        yes     yes
   odt         yes     yes
   rst         yes     yes
   latex       yes     yes
   epub        yes     yes
   ipynb       yes     yes
   txt         yes     yes
   pdf         NO      yes     ← write-only
   pptx        NO      yes     ← write-only, and not currently exposed
```

This is the root pattern behind findings 1 and 2, not two separate bugs.

---

## Finding 4: docx to markdown silently drops embedded images

```console
$ pandoc img.docx -t markdown
# T

![alt text](media/rId9.png){width="..." height="..."}
                ^^^^^^^^^^^^ referenced, but never written to disk

$ pandoc img.docx -t markdown --extract-media=./media
$ ls media/media
rId9.png                      ← now it exists
```

`--extract-media` is not exposed by the server, and there is no way to reach it except through a `defaults_file`.

**Impact.** On the inbound path, an agent converting a Word document receives broken image links **with no error and no warning**. It cannot detect that content is missing, so it reasons over an incomplete document and does not know it. Silent data loss is worse than a failed conversion.

Tracked in the `extract_media` issue.

---

## Finding 5: `reference_doc` is gated more narrowly than pandoc requires

[`server.py:188`](../../src/mcp_pandoc/server.py#L188) rejects `reference_doc` unless output is `docx`. Pandoc's `--reference-doc` applies to docx, odt, and pptx.

```console
$ pandoc a.md -o r.odt && pandoc a.md --reference-doc=r.odt -o out.odt
ODT REFDOC OK

$ pandoc a.md -o ref.pptx && pandoc a.md --reference-doc=ref.pptx -o out2.pptx
PPTX REFDOC OK
```

**Impact.** `reference_doc` is the parameter the reporter singled out as load-bearing, "the difference between a docx and a docx someone will actually accept". The same argument applies to a branded deck or an ODT house style. The restriction is ours.

---

## Finding 6: server-side warnings reach nobody

Four bare `print()` calls remain: [`server.py:209`](../../src/mcp_pandoc/server.py#L209), [`:280`](../../src/mcp_pandoc/server.py#L280), [`:282`](../../src/mcp_pandoc/server.py#L282), [`:285`](../../src/mcp_pandoc/server.py#L285).

**They are not corrupting the protocol today.** Verified by reading the SDK source: `mcp/server/stdio.py` takes a private duplicate of fd 1 for the wire and re-points fd 1 itself at stderr, so `print()` lands harmlessly on stderr.

Two reasons to change them anyway:

1. **Nobody sees them.** The MCP spec says clients MAY ignore stderr, and most do. A warning that reaches no one is not a warning.
2. **The safety net has documented fallback paths.** When the SDK cannot establish the diversion it serves the stream in place, exactly as v1 did. On that path a stray `print()` splices non-JSON into a stream the client parses strictly, and the connection wedges.

The SDK exposes `LoggingCapability` and `LoggingMessageNotification` for this.

---

## Finding 7: CI cannot see what a new user sees

This is the root cause of #40, not a contributing factor.

```
  CI                                  A real user
  ──                                  ───────────
  uv sync  → installs uv.lock         uvx  → fresh resolve, newest allowed
    └─ pinned mcp 1.x forever           └─ picked up mcp 2.0.0 → crash on import
```

`uv sync` installs the pinned lockfile. `uvx` resolves fresh. **Different programs, and only one was tested.**

### Why a PR check alone would not have caught it

```
  2025-08-29   v0.8.1 released ────┐
                                   │  ELEVEN MONTHS. Zero commits, zero PRs.
               mcp 2.0.0 ships ────┤  Every fresh install broken the whole time.
               issue #40 filed ────┤
  2026-07-31   v0.8.2 shipped ─────┘
```

Verified from `git log`. A PR check fires only when someone pushes, and nothing was pushed for eleven months. Both triggers are needed:

| Trigger | Catches |
|---|---|
| On PR | breaks we introduce, plus upstream breaks current at that moment |
| On schedule | upstream breaks during quiet periods ← the #40 window |

### Platform coverage

CI runs `ubuntu-latest` and Python 3.11 only. Both reporters of #40 were on **Windows 11 with Python 3.13**. `requires-python` is `>=3.11`, so 3.12 and 3.13 are supported and untested. The SDK contains Windows-specific stdio handle code that CI never executes.

---

## Finding 8: startup crashes are structurally invisible

Reported by the user:

> What made this bug hard to spot from the client side is that an import-time crash is completely silent, my agent just showed the server as not connecting, with no logs.

He is right, and it is not fixable in the server. The crash happens before the MCP session exists, so there is no protocol channel to report on. Python's traceback goes to stderr, and the [spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports) states:

> The server **MAY** write UTF-8 strings to its standard error (`stderr`) for logging purposes. Clients **MAY** capture, forward, or ignore this logging.

What can be improved is diagnosis cost. `__init__.py` currently has no argument handling at all, so `mcp-pandoc --version` silently starts a server and hangs.

---

## Summary

| # | Finding | Severity | Nature |
|---|---|---|---|
| 7 | CI does not install the way users install | P0 | Process. Caused #40 |
| 7 | CI covers neither Windows nor Python 3.13 | P0 | Process |
| 1 | `pdf` offered as an input format | P0 | Impossible promise to the model |
| 4 | docx→md silently drops images | P1 | Silent data loss |
| 2 | pptx output not exposed; pptx input impossible | P1 | Missing capability + invisible limit |
| 6 | Warnings reach nobody | P1 | Observability |
| 8 | Startup crashes invisible | P2 | Transport limit; reduce diagnosis cost |
| 5 | `reference_doc` gated to docx only | P2 | Unnecessary restriction |

Findings 1, 2, and 3 are the same underlying issue: **format support is directional, and the schema presents it as symmetric.**
