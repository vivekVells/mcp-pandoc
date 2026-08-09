# Audit: agent workflow gaps, August 2026

Evidence behind the issues opened after [#40](https://github.com/vivekVells/mcp-pandoc/issues/40). Issues link here rather than restating findings.

| | |
|---|---|
| **Prompted by** | [@pbarone's workflow description](https://github.com/vivekVells/mcp-pandoc/issues/40#issuecomment-5182935810) |
| **Audited** | mcp-pandoc v0.9.0 (`ef3de10`) |
| **Local toolchain** | pandoc **3.7.0.2** (released 2025-05-29), mcp python SDK 2.x, macOS |
| **Latest pandoc at time of audit** | 3.10.1 (2026-07-22) |
| **Date** | 2026-08-08. Revised 2026-08-08 after external review |

## Scope and limits

Read this before relying on anything below.

**The local pandoc used for testing is 14 months old.** Findings that say "pandoc cannot do X" are claims about **3.7.0.2 only**, and at least one of them was wrong as a general statement. Every capability claim below now carries the version it applies to. This is the main correction from review.

**The project declares no minimum pandoc version.** `pyproject.toml` lists `pandoc>=2.4`, which is the PyPI package *"Pandoc Documents for Python"*, a Python library. It is **not** the pandoc binary. Nothing in the project constrains which binary a user has installed, so "is X supported" currently has no answer. See Finding 9.

**Security is explicitly out of scope for this audit.** That is a deliberate exclusion, not an oversight, and it is arguably the more consequential gap: inbound documents come from third parties, the server takes arbitrary filesystem paths, and it executes user-supplied filter scripts. See [#36](https://github.com/vivekVells/mcp-pandoc/issues/36) and [#33](https://github.com/vivekVells/mcp-pandoc/issues/33). Those deserve their own audit against the same workflow.

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

## Finding 1: pandoc has no PDF reader, but the schema offers `pdf` as input

`input_format` includes `pdf` at [`server.py:114`](../../src/mcp_pandoc/server.py#L114).

```console
$ pandoc -f pdf b.pdf -t markdown
Unknown input format pdf
Pandoc can convert to PDF, but not from PDF.
```

**Version scope.** Checked the last 25 pandoc releases for any that added a PDF reader. None did. Unlike Finding 2, this is a general statement, not a property of 3.7.0.2.

**Impact.** The input schema is a promise made to a language model. A model reading `pdf` in the enum will attempt PDF input, fail, and often retry the same call. Failures are clean rather than data-corrupting, so this is **P1, not P0**.

Tracked in [#47](https://github.com/vivekVells/mcp-pandoc/issues/47).

---

## Finding 2: pandoc CAN read pptx since 3.8.3. This audit originally said otherwise, and was wrong

**Original claim, now retracted:** "Pandoc has no pptx reader, so pptx to markdown is impossible."

**Correction.** Pandoc **3.8.3**, released 2025-12-01, added a native PowerPoint reader:

> `Add `pptx` (PowerPoint) as new input format (Anton Antich).`
> `New module `Text.Pandoc.Readers.Pptx`, exporting `readPptx``

Verified against the pandoc release notes via the GitHub releases API. The same release added `asciidoc` and `xlsx` readers.

```console
# pandoc 3.7.0.2 (the version tested locally)
$ pandoc -f pptx deck.pptx -t markdown
Unknown input format pptx

# pandoc >= 3.8.3
pptx is a supported input format.
```

**What this means.**

| | |
|---|---|
| The user's inbound pptx step | **Works**, if he has pandoc 3.8.3 or newer. It was never impossible |
| Our exposure of pptx | Neither input nor output is exposed, in any pandoc version |
| The blocker | We cannot say "pptx input is supported" until the project declares a minimum pandoc version. See Finding 9 |
| `python-pptx` | **No longer relevant.** The original conclusion that a non-pandoc dependency would be required is withdrawn |

**Root cause of the error.** Testing against a 14-month-old local binary and reporting the result as a permanent property of pandoc rather than of that binary.

---

## Finding 3: format support is directional, and the schema presents it as symmetric

The principle holds. The matrix in the original audit did not, and is corrected here.

Both `input_format` and `output_format` use the same ten-value enum, which tells the model that anything readable is writable and vice versa.

| Format | Native reader | Native writer | Notes |
|---|---|---|---|
| markdown | yes | yes | |
| html | yes | yes | |
| docx | yes | yes | |
| odt | yes | yes | |
| rst | yes | yes | |
| latex | yes | yes | |
| epub | yes | yes | |
| ipynb | yes | yes | |
| **txt** | **NO** | via alias | See Finding 4. Not a pandoc format in either direction |
| **pdf** | **NO** | yes | Write-only. No reader in any release |
| **pptx** | **>= 3.8.3** | yes | Not exposed by this project in either direction |

The relevant distinction is four-way, not two-way: **native reader**, **native writer**, **project alias or extension inference**, and **minimum pandoc version**.

---

## Finding 4: `input_format: "txt"` fails, and the schema offers it

Not in the original audit. Found during review.

`txt` is not a pandoc format in either direction. [`server.py:177`](../../src/mcp_pandoc/server.py#L177) translates it to `plain` **for output only**. There is no equivalent translation for input.

```console
$ pandoc --list-input-formats | grep -cx "txt"
0
```

Against the running server:

```console
$ contents="hello world", input_format="txt", output_format="html"
Error converting contents from txt to html: Invalid input format! Got "txt"
but expected one of these: biblatex, bibtex, bits, commonmark, ...
```

**Why it looks like it works.** `.txt` **files** convert fine, because the `input_file` branch at [`server.py:359`](../../src/mcp_pandoc/server.py#L359) never passes `input_format` to pypandoc. Pandoc infers from the extension and falls back to markdown. So the parameter is silently ignored on the file path and hard-fails on the inline-content path.

Two defects in one: an enum value that cannot work, and a parameter that is ignored in one branch and honoured in the other.

---

## Finding 5: docx to markdown silently drops embedded images

```console
$ pandoc img.docx -t markdown
![alt text](media/rId9.png){width="..." height="..."}
                ^^^^^^^^^^^^ referenced, but never written to disk

$ pandoc img.docx -t markdown --extract-media=./media
$ ls media/media
rId9.png                      ← now it exists
```

`--extract-media` is not exposed and is reachable only through a `defaults_file`.

**Impact.** An agent converting an inbound Word document receives broken image links **with no error and no warning**. It cannot detect that content is missing, so it reasons over an incomplete document and does not know it.

**Evidence gap, from review.** This was reproduced with a synthetic one-pixel PNG embedded in a generated docx. No representative fixture is committed, so the result cannot be independently re-run. A real-world docx fixture should be added before designing the fix.

**On the API question.** Review raised that a ninth parameter conflicts with the "eight parameter" contract. It does not. `additionalProperties: false` rejects properties *clients send that we do not know*. Adding a new optional property to the published schema is additive and backwards compatible. The contract is about not removing or renaming. The open design question is whether extraction should be implicit or explicit, and where files land, not whether a parameter may be added.

Tracked in [#48](https://github.com/vivekVells/mcp-pandoc/issues/48).

---

## Finding 6: `reference_doc` is gated more narrowly than pandoc requires

[`server.py:188`](../../src/mcp_pandoc/server.py#L188) rejects `reference_doc` unless output is `docx`. Pandoc's `--reference-doc` applies to docx, odt, and pptx.

```console
$ pandoc a.md -o r.odt && pandoc a.md --reference-doc=r.odt -o out.odt      # succeeds
$ pandoc a.md -o ref.pptx && pandoc a.md --reference-doc=ref.pptx -o out2.pptx  # succeeds
```

Verified on 3.7.0.2, and this scope has been stable across releases.

**Impact.** `reference_doc` is the parameter the reporter singled out as load-bearing, "the difference between a docx and a docx someone will actually accept". The same argument applies to a branded deck or an ODT house style. The restriction is ours, not pandoc's.

Tracked in [#52](https://github.com/vivekVells/mcp-pandoc/issues/52).

---

## Finding 7: bare `print()` for diagnostics, and the fix is stderr, not MCP logging

Four bare `print()` calls remain: [`server.py:209`](../../src/mcp_pandoc/server.py#L209), [`:280`](../../src/mcp_pandoc/server.py#L280), [`:282`](../../src/mcp_pandoc/server.py#L282), [`:285`](../../src/mcp_pandoc/server.py#L285).

**They are not corrupting the protocol.** Verified by reading the SDK source: `mcp/server/stdio.py` takes a private duplicate of fd 1 for the wire and re-points fd 1 itself at stderr, so `print()` lands on stderr. There are documented fallback paths where the diversion is not established and the stream is served in place; on those, a stray `print()` would splice non-JSON into a stream the client parses strictly.

**Correction from review: do not migrate to MCP logging notifications.** The original audit recommended `notifications/message`. That is now against spec guidance. From the [2026-07-28 logging specification](https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/logging):

> **Deprecated**: The Logging feature is deprecated as of protocol version `2026-07-28` ([SEP-2577](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2577)). [...] New implementations **SHOULD NOT** adopt it; existing implementations **SHOULD** migrate to logging to `stderr` for stdio transports, or to [OpenTelemetry](https://opentelemetry.io/) for structured observability.

**Also corrected:** the original audit asserted "most clients ignore stderr". That was unsupported. What the spec actually says is that clients **MAY** capture, forward, or ignore stderr, and current MCP debugging guidance says stdio hosts capture it.

**Revised recommendation, split by audience:**

| Audience | Channel |
|---|---|
| The model, for anything affecting the result | Include it in the tool result text. Dropped media, ignored parameters, format fallbacks |
| A human debugging | `logging` module to stderr, with levels. Not `print()` |
| Neither | Delete the message |

Tracked in [#50](https://github.com/vivekVells/mcp-pandoc/issues/50), which needs redesign along these lines.

---

## Finding 8: CI does not install the way users install

**Corrected causality.** The root cause of #40 was the **uncapped `mcp` dependency**. Lockfile-based CI was a **detection gap**, not the cause. The original audit conflated the two.

```
  CI                                  A real user
  ──                                  ───────────
  uv sync  → installs uv.lock         uvx  → fresh resolve, newest allowed
    └─ stayed on mcp 1.x                └─ resolved to mcp 2.0.0 → crash on import
```

**Corrected timeline.** The original audit claimed every fresh install was broken for eleven months. That is false.

| Event | Date | Source |
|---|---|---|
| v0.8.1 released | 2025-08-29 | git tag |
| Last commit before the gap | 2025-09-15 | git log |
| **mcp 2.0.0 released** | **2026-07-28** | [PyPI](https://pypi.org/project/mcp/2.0.0/) |
| #40 filed | 2026-07-29 | GitHub |
| v0.8.2 fix shipped | 2026-07-31 | git tag |

**The break window was approximately three days, not eleven months.** The quiet period in the repo was real, roughly ten months with no commits from 2025-09-15, but the two are separate facts and the original audit merged them. It also incorrectly stated there were zero commits after v0.8.1; there were 11, through 2025-09-15.

**An honest consequence for the scheduled-job recommendation.** Users reported this within one day of the break. A weekly scheduled check would average 3.5 days and would have been **slower than the community**. The argument for scheduled fresh-resolution testing is therefore not "it would have caught #40 sooner". It is that it gives detection you control, for breaks that are subtler than a startup crash and that users may never report. That is a weaker claim than the original audit made, and it should be stated as the weaker claim.

**Platform coverage.** CI runs `ubuntu-latest` and Python 3.11 only. `requires-python` is `>=3.11`, so 3.12 and 3.13 are untested. @pbarone reported Windows 11 with Python 3.13. @Andrea-encrypted reported Windows without specifying a Python version. The original audit's "both reporters on Windows 11 and Python 3.13" overstated the second report.

Tracked in [#45](https://github.com/vivekVells/mcp-pandoc/issues/45) and [#46](https://github.com/vivekVells/mcp-pandoc/issues/46).

---

## Finding 9: no minimum pandoc binary version is declared

Not in the original audit. This is the blocker for Finding 2 and it makes several capability questions unanswerable.

```toml
dependencies = [
  "pandoc>=2.4",     # ← the PyPI package "Pandoc Documents for Python", a Python library
  "pypandoc>=1.14",  # ← wrapper that shells out to the binary
]
```

Neither constrains the **pandoc binary** the user has installed. Consequences:

- "Does mcp-pandoc support pptx input" has no answer. It depends on a binary version we neither declare nor check.
- A user on pandoc 2.x and a user on 3.10.1 get materially different capabilities from the same server version, with no signal about why.
- Enum values cannot be gated on capability, because capability is unknown at startup.

Until a minimum is declared and checked, any format-support claim in the README is conditional on something unstated.

---

## Finding 10: startup crashes cannot be reported through MCP

Reported by the user:

> What made this bug hard to spot from the client side is that an import-time crash is completely silent, my agent just showed the server as not connecting, with no logs.

Accurate as far as the protocol goes. The crash happens before the MCP session exists, so there is no protocol channel to report on.

**Qualified from review.** The traceback does reach stderr, and current MCP debugging guidance says stdio hosts capture stderr. So the failure is not universally invisible; it was invisible in the client he was using. A diagnostics command is **optional product work**, not a necessary consequence of the transport design. `--version` and better troubleshooting docs are the smaller first step.

`__init__.py` currently has no argument handling, so `mcp-pandoc --version` silently starts a server and hangs.

Tracked in [#51](https://github.com/vivekVells/mcp-pandoc/issues/51).

---

## Summary

| # | Finding | Priority | Confidence |
|---|---|---|---|
| 9 | No minimum pandoc version declared | P0 | Verified. Blocks 2 and 3 |
| 8 | CI does not install the way users install | P1 | Verified. Weaker rationale than originally stated |
| 8 | CI covers neither Windows nor Python 3.13 | P1 | Verified |
| 5 | docx to markdown silently drops images | P1 | Verified. Needs a committed fixture |
| 4 | `input_format: "txt"` fails; ignored on the file branch | P1 | Verified against the running server |
| 1 | `pdf` offered as an input format | P1 | Verified across all releases |
| 2 | pptx supported by pandoc >= 3.8.3, exposed by us in neither direction | P2 | Verified. **Corrects the original audit** |
| 7 | Diagnostics via `print()` | P2 | Verified. Fix is stderr, not MCP logging |
| 6 | `reference_doc` gated to docx only | P2 | Verified |
| 10 | Startup crashes invisible in some clients | P3 | Qualified |

**Out of scope and unaddressed:** the trust boundary. Inbound documents originate from third parties, the server accepts arbitrary filesystem paths, and it executes user-supplied filter scripts. See [#36](https://github.com/vivekVells/mcp-pandoc/issues/36) and [#33](https://github.com/vivekVells/mcp-pandoc/issues/33).

## What has been acted on

The audit itself is a record and is not rewritten. This table tracks what shipped.

| Finding | Status | Where |
|---|---|---|
| 6, `reference_doc` gated to docx only | **Done** in v0.10.0 | Widened to docx and odt in [#59](https://github.com/vivekVells/mcp-pandoc/pull/59). That PR also surfaced a failure the audit missed: pandoc does not check that the reference document matches the writer, so a `.docx` reference against odt output wrote a file pandoc could not read, and a `.odt` reference against docx output was silently discarded, both reported as success. Now rejected before conversion |
| 3, format support is directional but the schema is symmetric | **Partly done** in v0.11.0 | The shared enum was split into `INPUT_FORMATS` and `OUTPUT_FORMATS`. `pdf` is still wrongly listed as an input format; see [#47](https://github.com/vivekVells/mcp-pandoc/issues/47) |
| 2, pptx supported by pandoc but exposed in neither direction | **Half done** in v0.11.0 | pptx **output** shipped, and needs no minimum pandoc version: the writer has existed since pandoc 2.0.5 (2017). pptx **input** needs pandoc >= 3.8.3 and remains blocked on Finding 9 |
| 9, no minimum pandoc binary version declared | **Open**, with a decision | [#54](https://github.com/vivekVells/mcp-pandoc/issues/54) carries the evidence. A hard floor is rejected: Ubuntu 24.04 ships pandoc 3.1.3 and Debian trixie 3.1.11.1, so a floor at 3.8.3 would break users following our own install instructions, and would fail our own CI. The direction is per-feature minimums checked at point of use |
| 4, `input_format: "txt"` fails | **Open** | [#57](https://github.com/vivekVells/mcp-pandoc/issues/57). Cheaper now that the enums are split |
| 7, bare `print()` | **Open** | [#50](https://github.com/vivekVells/mcp-pandoc/issues/50) |
| 5, docx to markdown drops images | **Open** | [#48](https://github.com/vivekVells/mcp-pandoc/issues/48) |
| 8, CI install and platform coverage | **Partly done** | `pre-commit` now runs in CI. Fresh-resolution install and the Windows and Python 3.13 matrix remain open in [#45](https://github.com/vivekVells/mcp-pandoc/issues/45) and [#46](https://github.com/vivekVells/mcp-pandoc/issues/46) |

New since the audit: [#60](https://github.com/vivekVells/mcp-pandoc/issues/60), the reference-document type check is still bypassable through `reference-doc` inside a `defaults_file`.

## Revision history

| Date | Change |
|---|---|
| 2026-08-08 | Initial audit |
| 2026-08-08 | Revised after external review. Retracted the pptx impossibility claim (pandoc 3.8.3 added a reader). Corrected the #40 timeline from eleven months to roughly three days and separated root cause from detection gap. Corrected the format matrix and added the `txt` reader defect. Reversed the MCP logging recommendation, now deprecated by spec. Added the missing minimum-pandoc-version finding. Scoped out security explicitly. Corrected the environment claim about the second reporter. |
