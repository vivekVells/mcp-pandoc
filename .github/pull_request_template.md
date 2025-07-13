## Summary

Brief description of what this PR changes and why.

## Essential Checklist

- [ ] Tests pass locally (`uv run pytest tests/test_conversions.py`)
- [ ] Code follows existing patterns in `src/mcp_pandoc/server.py`
- [ ] Documentation updated (if needed)
- [ ] Screenshots included below for visual verification

## Screenshots (Required)

Please include screenshots to help reviewers verify your changes:

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

- [ ] New format added to `SUPPORTED_FORMATS` in server.py
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
