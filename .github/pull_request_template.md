## Summary

Brief description of what this PR changes and why.

## Environment

Format support depends on the pandoc binary you have installed, which this project does not pin. Please fill this in.

- pandoc: <!-- first line of `pandoc --version` -->
- OS:
- Python:

## Essential Checklist

- [ ] `uv run pytest` passes (paste the summary line below)
- [ ] `uv run ruff check .` passes
- [ ] `uv run yamllint .` passes
- [ ] `uv run pre-commit run --all-files` passes
- [ ] Code follows existing patterns in `src/mcp_pandoc/server.py`
- [ ] Documentation updated (if needed)
- [ ] Every format I documented is present in the matching enum in `server.py`, verified in the direction I claimed it

## Screenshots (if your change has visible output)

Not needed for backend or validation-only changes; paste the test output instead.

**For new features or format support:**
- [ ] Before/after conversion examples showing the new functionality
- [ ] Sample input and output files

**For bug fixes:**
- [ ] Screenshots showing the error before the fix
- [ ] Screenshots showing the fix working correctly

**For all changes:**
- [ ] Proof that existing functionality still works (test a few conversions)

<!-- Upload screenshots here or link to them -->

## Additional Context

<details>
<summary>🔄 Format Support Changes (expand if adding/modifying formats)</summary>

- [ ] New format added to the `supported_formats` set in `handle_call_tool` (server.py)
- [ ] Added only to the `input_format` / `output_format` enum direction that was verified
- [ ] Bidirectional conversion testing included
- [ ] Test fixtures added to `tests/fixtures/`
- [ ] Conversion matrix in README.md updated
- [ ] CHEATSHEET.md examples added

</details>

<details>
<summary>⚠️ Breaking Changes (expand if applicable)</summary>

- [ ] Breaking changes clearly documented
- [ ] Migration guide provided (if needed)
- [ ] Version bump considerations noted

</details>

---

Any additional notes for reviewers.
