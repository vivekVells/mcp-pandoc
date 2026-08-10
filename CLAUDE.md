# CLAUDE.md - mcp-pandoc Development Guide

*Last Updated: 2025-07-13*

## Project Overview

**mcp-pandoc** is a Model Context Protocol (MCP) server that provides document format conversion capabilities using Pandoc. This project enables seamless bidirectional conversion between 10+ document formats including Markdown, HTML, PDF, DOCX, LaTeX, EPUB, and more.

### Core Architecture
- **MCP Server**: Implements JSON-RPC 2.0 protocol for tool-based document conversion
- **Primary Tool**: `convert-contents` - handles all format conversions with comprehensive validation
- **Backend Engine**: Pandoc with pypandoc Python wrapper
- **Special Features**: Reference document styling for DOCX, ODT and PPTX, advanced format support

## 🎯 Project Philosophy & Decision Framework

### Core Principle: "Pandoc, Perfected for MCP"

mcp-pandoc follows the "iPhone approach" - **do fewer things, but do them perfectly**. We are the definitive Pandoc MCP server for document format conversion, not a universal document processor.

### Decision Framework for New Features

When evaluating any new feature request, assess against these criteria:

**✅ Green Light Criteria:**
- Native Pandoc capability that we're not fully leveraging
- High user value with low to medium implementation complexity
- Improves reliability or performance of existing features
- Enhances the core document conversion workflow

**⚠️ Yellow Light Criteria (Requires Strong Justification):**
- Adds new dependencies but provides significant user value
- Complex implementation but addresses critical user need
- Extension of Pandoc capabilities through well-established patterns

**❌ Red Light Criteria (Default: No):**
- Requires external tools not related to Pandoc
- Significant maintenance burden for niche use cases
- Better served by specialized servers in the MCP ecosystem
- Scope creep beyond document format conversion

### Maintenance Philosophy
- **Focused Excellence > Feature Breadth**
- **Reliability > Cutting-Edge Features**
- **Pandoc-Native > External Integrations**
- **Sustainable Development > Complex Dependencies**

### Examples of This Philosophy in Action

**✅ Good Additions (Pandoc-Native):**
- Citation & bibliography support (built-in citeproc)
- Math equation processing (native Pandoc capability)
- Custom template support (core Pandoc feature)
- Enhanced metadata handling (Pandoc strength)

**❌ Avoided Complexity:**
- Native diagram support (external Node.js dependency)
- Multi-format media conversion (belongs in specialized servers)
- Complex external tool integrations (maintenance burden)
- Custom syntax extensions (scope creep)

*Note: Features outside document conversion scope should be implemented in specialized servers rather than added to mcp-pandoc.*

## Development Environment Setup

### Required Dependencies
```bash
# Core dependencies (required)
brew install pandoc uv                    # macOS
sudo apt-get install pandoc && pip install uv  # Ubuntu/Debian

# PDF support (optional but recommended)
brew install texlive                      # macOS
sudo apt-get install texlive-xetex      # Ubuntu/Debian
```

### Development Workflow
```bash
# Setup and sync dependencies
uv sync

# Run locally for testing
uv run mcp-pandoc

# Run comprehensive test suite
uv run pytest tests/test_conversions.py

# Build for distribution
uv build

# Publish to PyPI
uv publish
```

### MCP Inspector for Debugging
```bash
npx @modelcontextprotocol/inspector uv --directory $(pwd) run mcp-pandoc
```

## Project Structure & Key Files

```
/mcp-pandoc/
├── src/mcp_pandoc/
│   ├── __init__.py              # Entry point with async main()
│   └── server.py                # Core MCP server implementation
├── tests/
│   ├── fixtures/                # Test input files for all formats
│   ├── output/                  # Test output directory
│   └── test_conversions.py      # Parametrized bidirectional testing
├── demo/                        # Screenshots and demo assets
├── README.md                    # Comprehensive user documentation
├── CHEATSHEET.md               # Quick reference guide
├── pyproject.toml              # Python project configuration
└── smithery.yaml               # MCP server distribution config
```

## MCP Protocol Best Practices

### Tool Definition Standards
- **JSON Schema Validation**: All parameters use comprehensive JSON Schema with enum validation
- **Error Handling**: Descriptive error messages with actionable guidance
- **Type Safety**: Full type hints throughout codebase
- **Protocol Compliance**: Strict JSON-RPC 2.0 adherence

### Security Implementation
```python
# File path validation pattern (server.py:161-162)
if reference_doc and not os.path.exists(reference_doc):
    raise ValueError(f"Reference document not found: {reference_doc}")

# Format validation pattern (server.py:165-167)
OUTPUT_FORMATS = ("markdown", "html", "pdf", "docx", "rst", "latex", "epub", "txt", "ipynb", "odt", "pptx")
if output_format not in OUTPUT_FORMATS:
    raise ValueError(f"Unsupported output format: '{output_format}'")
```

### Tool Architecture Pattern
- **Parameter Validation**: oneOf/allOf JSON Schema constraints for required parameters
- **Conditional Requirements**: Advanced formats require output_file paths
- **Reference Document Support**: DOCX, ODT and PPTX styling, with the reference type validated against the output format

## Testing Strategy

### Comprehensive Format Testing
```python
# Parametrized testing pattern (test_conversions.py:28-29)
@pytest.mark.parametrize("from_format", FORMATS)
@pytest.mark.parametrize("to_format", FORMATS)
def test_bidirectional_conversions(from_format, to_format):
```

### Test Coverage Areas
- **All Format Combinations**: every readable format against every writable one. pdf and pptx are write-only and are skipped as sources
- **Fixture Management**: Pre-created test files for each format
- **Output Validation**: File existence and basic content verification
- **Edge Cases**: PDF special handling, format-specific requirements

### Test Execution
```bash
# Run all tests
uv run pytest tests/test_conversions.py

# Run with verbose output
uv run pytest tests/test_conversions.py -v

# Run specific format combinations
uv run pytest tests/test_conversions.py -k "md_to_html"
```

## Development Workflow - IMPORTANT

### 🚨 CRITICAL: Always Use Feature Branches + Pull Requests

**NEVER commit directly to main unless explicitly requested by the user.**

**Correct Workflow:**
1. Create feature branch: `git checkout -b feature/description`
2. Make changes and commit to feature branch
3. Push feature branch: `git push -u origin feature/description`
4. Create pull request: `gh pr create`
5. Wait for user approval before merging

**Only commit directly to main when:**
- User explicitly says "commit to main" or "push directly"
- User says "skip the PR process"
- Emergency fixes that user specifically requests

## Pull Request Review Guidelines

### 🔄 Pre-Review Automated Checks
- [ ] **All tests pass**: `uv run pytest tests/test_conversions.py`
- [ ] **Code builds successfully**: `uv build`
- [ ] **No security vulnerabilities**: Code review for file path handling
- [ ] **Type hints present**: All new functions have proper type annotations

### 📋 Manual Review Checklist

#### Functionality Review
- [ ] **New features work correctly**: Test manually with MCP Inspector
- [ ] **Existing functionality preserved**: No regression in current features
- [ ] **Error handling implemented**: Proper exception handling and user messages
- [ ] **Performance maintained**: No significant slowdowns introduced

#### Code Quality Standards
- [ ] **Follows existing patterns**: Consistent with `src/mcp_pandoc/server.py` style
- [ ] **Async/await usage**: Proper async patterns for MCP operations
- [ ] **JSON Schema validation**: New parameters include proper schema definitions
- [ ] **Security practices**: File path validation, input sanitization

#### Documentation Requirements
- [ ] **README.md updated**: New features documented with examples
- [ ] **CHEATSHEET.md updated**: Quick reference examples added
- [ ] **Tool descriptions updated**: Comprehensive parameter documentation
- [ ] **Docstrings added**: Function-level documentation for new code

#### Testing Requirements
- [ ] **New tests added**: Test coverage for new functionality
- [ ] **Existing tests pass**: No broken existing test cases
- [ ] **Edge cases covered**: Error conditions and boundary cases tested
- [ ] **Format compatibility**: Bidirectional conversion matrix maintained

### 🔍 Regression Prevention Checklist
- [ ] **All formats still supported**: md, html, txt, docx, odt, rst, latex, epub, ipynb readable and writable; pdf and pptx writable only
- [ ] **Reference document styling works**: DOCX template functionality preserved
- [ ] **File path requirements enforced**: Advanced formats still require output_file
- [ ] **Error messages remain helpful**: User-friendly error guidance maintained

### 🚨 Critical Review Areas

#### Security Validation
```bash
# Check for proper file path validation
grep -n "os.path.exists" src/mcp_pandoc/server.py
grep -n "outputfile=" src/mcp_pandoc/server.py
```

#### Format Support Validation
```bash
# Verify supported formats list is maintained
grep -n "INPUT_FORMATS\|OUTPUT_FORMATS" src/mcp_pandoc/server.py
grep -n "ADVANCED_FORMATS\|REFERENCE_DOC_FORMATS" src/mcp_pandoc/server.py
```

## Common Development Patterns

### Error Handling Pattern
```python
try:
    # Conversion operation
    converted_output = pypandoc.convert_text(...)
except Exception as e:
    error_msg = f"Error converting {input_format} to {output_format}: {str(e)}"
    raise ValueError(error_msg)
```

### JSON Schema Validation Pattern
```python
"allOf": [
    {
        "if": {
            "properties": {
                "output_format": {
                    "enum": ["pdf", "docx", "rst", "latex", "epub"]
                }
            }
        },
        "then": {
            "required": ["output_file"]
        }
    }
]
```

### Async MCP Server Pattern
```python
@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
```

## Key Maintenance Notes

### Format Support Matrix
- **Directional**: `INPUT_FORMATS` and `OUTPUT_FORMATS` are separate constants and must stay separate. Pandoc reads and writes different sets
- **Write-only**: pdf (no pandoc reader in any release) and pptx (reader added in pandoc 3.8.3, not yet exposed; see #54)
- **Advanced Formats**: `ADVANCED_FORMATS` covers pdf, docx, odt, pptx, rst, latex, epub, all of which require an output_file
- **Basic Formats**: md, html, txt, ipynb are returned inline
- **Reference Documents**: `REFERENCE_DOC_FORMATS` covers docx, odt and pptx. The reference file must match the output format; pandoc does not check this and fails silently when it is wrong

### Dependency Management
- **Pandoc**: Core conversion engine, must be system-installed
- **TeX Live**: Required for PDF generation (xelatex engine)
- **UV**: Package manager for Python dependencies and distribution

### Performance Considerations
- **File I/O**: All conversions involve disk operations
- **Memory Usage**: Large documents may require significant memory
- **Error Recovery**: Robust error handling prevents server crashes

## Quick Reference Commands

```bash
# Development
uv sync                                    # Sync dependencies
uv run mcp-pandoc                         # Run server locally
uv run pytest tests/test_conversions.py  # Run tests

# Distribution
uv build                                  # Build package
uv publish                               # Publish to PyPI

# Debugging
npx @modelcontextprotocol/inspector uv --directory $(pwd) run mcp-pandoc

# Testing specific formats
uv run pytest tests/test_conversions.py -k "md_to_pdf"
uv run pytest tests/test_conversions.py -v --tb=short
```

## 📚 Lessons Learned from PR Review Process

*Added 2025-07-13 based on PR #24 review experience*

### ⚠️ Critical Review Gaps Identified

During the review of PR #24 (Pandoc defaults file support), several systematic gaps were identified that must be prevented in future PRs:

#### 1. Version Bump Analysis
**Problem**: Incorrectly justified 0.4.0 → 0.6.0 jump
**Root Cause**: Failed to apply semantic versioning principles rigorously
**Prevention**:
- Always verify version bump follows semver (MAJOR.MINOR.PATCH)
- Document version justification in PR description
- New features = MINOR bump, bug fixes = PATCH bump, breaking changes = MAJOR bump

#### 2. Documentation Assessment
**Problem**: Failed to identify missing documentation coverage
**Root Cause**: Didn't systematically check all user-facing documentation
**Prevention**:
- **Mandatory Documentation Checklist**:
  - [ ] README.md parameter documentation updated
  - [ ] CHEATSHEET.md examples added for new features
  - [ ] Version references updated across all docs
  - [ ] Error troubleshooting section updated

#### 3. Test Organization Strategy
**Problem**: Created PR-specific test files with poor long-term naming
**Root Cause**: Focused on immediate testing needs vs. sustainable maintenance
**Prevention**:
- Use feature-based test organization (`test_advanced_features.py`)
- Avoid PR-specific naming (`test_pr24_features.py` ❌)
- Group tests by functional area, not implementation timeline
- Consider maintainer perspective for test file longevity

#### 4. Feature Value Communication
**Problem**: Failed to explain business value and real-world applications
**Root Cause**: Didn't research the Pandoc ecosystem thoroughly
**Prevention**:
- Research feature's real-world usage patterns
- Document specific user problems the feature solves
- Include workflow examples in review analysis
- Verify feature fits the project's scope and vision

#### 5. Temporal Bias in Documentation
**Problem**: Added "NEW" markers, version annotations, and star emojis to CHEATSHEET.md
**Root Cause**: Feature announcement mentality instead of timeless reference approach
**Prevention**:
- Write documentation as if features always existed
- Organize by user workflows, not feature chronology
- Remove version-specific annotations from user-facing docs
- Test: Would someone discovering the project in 2027 be confused?

#### 6. Contributor Experience Balance
**Problem**: Created overwhelming templates and processes that discourage participation
**Root Cause**: Maintainer anxiety leading to over-documentation of requirements
**Prevention**:
- Use progressive disclosure (simple paths for simple contributions)
- Distinguish between essential items (4-8) and detailed requirements
- Create tiered requirements based on contribution complexity
- Smart linking to detailed guidance instead of inline overwhelm

#### 7. Execution vs Analysis Gap
**Problem**: Identified 0.4.0 → 0.6.0 version issue but failed to actually fix it
**Root Cause**: Got distracted by process improvements and didn't systematically verify execution
**Prevention**:
- Create execution verification checklist (not just analysis checklist)
- Document the problem ≠ Fix the problem - must verify actual resolution
- Systematic review of all identified issues before completion
- Don't let meta-work distract from core technical fixes

#### 8. Framework Creation ≠ Framework Application
**Problem**: Created comprehensive PR Review Execution Framework but failed to apply it to own README.md work
**Root Cause**: Assumed that creating the right process was sufficient without self-application
**Prevention**:
- **Self-validation requirement**: Must run own frameworks on own work before declaring completion
- **Practice what you document**: Every process created must be immediately applied to current work
- **Meta-accountability**: The creator of standards must demonstrate compliance first
- **Process validation**: If I can't follow my own framework, it's not ready for others

### 🔧 Process Improvements Implemented

#### Systematic Prevention Mechanisms

1. **CONTRIBUTING.md**: Progressive disclosure approach
   - Quick start section for simple contributions
   - Tiered requirements based on contribution complexity
   - Welcoming tone with clear paths for different contribution types
   - Detailed Feature PR Requirements section for substantial changes only

2. **PR Template**: Lightweight with smart linking
   - Reduced from 50+ items to 4 essential checkboxes
   - Conditional sections based on contribution type
   - Smart linking to detailed requirements in CONTRIBUTING.md
   - Encouraging tone focused on what's needed

3. **Documentation Standards**: Timeless, user-centric approach
   - CHEATSHEET.md organized by user workflows, not feature chronology
   - Removed all temporal markers (NEW, version annotations, star emojis)
   - Integrated all features as unified capabilities
   - Focus on practical usage without feature history bias

#### Enhanced Review Criteria

**Before Approving Any PR**:
- [ ] **Feature Justification**: Clear explanation of business value
- [ ] **Version Analysis**: Proper semantic versioning applied
- [ ] **Documentation Completeness**: All user-facing docs updated
- [ ] **Test Strategy**: Sustainable test organization
- [ ] **Backwards Compatibility**: No unintentional breaking changes
- [ ] **Security Assessment**: Input validation and error handling
- [ ] **Performance Impact**: No significant regressions

**Execution Verification Checklist**:
- [ ] **All identified issues actually fixed**: Don't just document problems, verify resolution
- [ ] **Version changes applied**: If version discussed, verify pyproject.toml updated
- [ ] **Tests updated**: If version changed, verify test expectations updated
- [ ] **Dependencies synced**: Run `uv sync` if version changed
- [ ] **Documentation consistency**: All references to versions are accurate
- [ ] **No execution gaps**: Every analysis finding has corresponding implementation

### 🎯 Maintainer Mindset Principles

#### Long-term Maintenance Focus
- **Test Naming**: Think 2+ years ahead for test file organization
- **Documentation**: Write for users who will discover features later
- **Version Strategy**: Protect users from unnecessary breaking changes
- **Dependency Assessment**: Consider maintenance burden of new deps

#### User-Centric Design
- **Timeless Documentation**: Write as if features always existed
- **Workflow Organization**: Structure by user goals, not implementation details
- **Progressive Disclosure**: Simple paths for simple needs, detailed guidance when needed
- **Remove Temporal Bias**: Avoid "new" vs "old" feature distinctions

#### Quality Debt Prevention
- **Systematic Reviews**: Use checklists to prevent oversight
- **Prevention Over Reaction**: Create tools to guide contributors
- **Knowledge Transfer**: Document decisions for future maintainers
- **Standard Enforcement**: Consistent application of quality standards
- **Contributor Experience**: Balance quality with accessibility

### 📊 Success Metrics

**PR Review Quality Indicators**:
1. **Complete Documentation**: No missing user examples or parameter docs
2. **Proper Versioning**: Semantic version bumps with clear justification
3. **Comprehensive Testing**: Feature coverage without technical debt
4. **Clear Value Proposition**: Business justification for all features
5. **Security Validation**: Input handling and error management verified

### 🔄 Continuous Improvement

This section will be updated as we learn from future PR reviews. Key focus areas:
- Monitor contributor adoption of new guidelines
- Collect feedback on process effectiveness
- Refine documentation based on common gaps
- Enhance automation where possible

**Next Review Checkpoints**: Update this section after every major PR review to capture new lessons and process refinements.

## 🔄 PR Review Execution Framework

*Added 2025-07-13 - Practical workflow to ensure systematic, thorough reviews*

### Phase 1: Initial Assessment (5-10 minutes)

#### Quick Scan
1. **PR Type Identification**:
   - Bug fix (low complexity) → Use Essential Checklist only
   - Documentation (low complexity) → Focus on clarity and examples
   - New feature (high complexity) → Full Feature PR Requirements
   - Maintenance (medium complexity) → Focus on backward compatibility

2. **Scope Validation**:
   - Single, focused change ✅ → Proceed with review
   - Multiple unrelated changes ❌ → Request scope reduction
   - Unclear motivation → Request clarification before detailed review

3. **Initial Red Flags**:
   - Version bump without justification → Stop, request explanation
   - Missing tests for new functionality → Flag for detailed review
   - New dependencies without rationale → Flag for justification

#### Set Review Expectations
- **Estimated review time**: 10 min (bug fix) to 60 min (major feature)
- **Execution checkpoint reminder**: Every analysis finding MUST have corresponding fix verification
- **Focus area**: Prioritize user impact over internal refactoring

### Phase 2: Systematic Analysis (15-45 minutes)

#### Technical Review Sequence
1. **Version Analysis** (2 minutes):
   - Check pyproject.toml version change
   - Verify semantic versioning: patch/minor/major appropriateness
   - **MANDATORY**: If version discussed, verify pyproject.toml actually updated

2. **Code Quality Review** (10-20 minutes):
   - Type hints present for new functions
   - Error handling with user-friendly messages
   - Security: file path validation, safe YAML loading
   - Performance: no blocking operations in async code

3. **Testing Strategy** (10-15 minutes):
   - New functionality has corresponding tests
   - Test organization: feature-based naming, not PR-specific
   - Backward compatibility: existing tests still pass
   - **EXECUTION CHECK**: Run tests if any concerns

4. **Documentation Assessment** (10-15 minutes):
   - README.md: new parameters documented in Tools section
   - CHEATSHEET.md: practical examples for new features
   - No temporal bias: avoid "NEW" markers or version annotations
   - **EXECUTION CHECK**: Verify examples actually work

#### Decision Priority Framework
**High Priority (Must Fix)**:
- Security vulnerabilities
- Breaking changes without migration path
- Incorrect semantic versioning
- Missing documentation for user-facing features

**Medium Priority (Should Fix)**:
- Test organization improvements
- Error message clarity
- Performance optimizations
- Dependency justifications

**Low Priority (Nice to Have)**:
- Code style consistency
- Additional test coverage
- Documentation improvements beyond requirements

### Phase 3: Execution Verification (5-15 minutes)

#### Mandatory Verification Gates
Cannot approve PR without verifying:

1. **Version Consistency Check**:
   - [ ] If version discussed → pyproject.toml actually updated
   - [ ] Test expectations updated to match new version
   - [ ] Dependencies synced with `uv sync`

2. **Documentation Completeness**:
   - [ ] New parameters in README.md Tools section
   - [ ] Working examples in CHEATSHEET.md
   - [ ] No temporal markers or version-specific annotations

3. **Testing Verification**:
   - [ ] New tests exist for new functionality
   - [ ] Test naming is sustainable (feature-based, not PR-specific)
   - [ ] All tests pass: `uv run pytest tests/test_conversions.py`

4. **Backward Compatibility**:
   - [ ] Existing functionality preserved
   - [ ] No unintentional breaking changes
   - [ ] Migration path provided if breaking changes necessary

#### Final Execution Checklist
Before marking "Changes Requested" or "Approved":
- [ ] **Every identified issue has corresponding action item**
- [ ] **Analysis findings verified with actual code/doc checks**
- [ ] **Priority level assigned to each requested change**
- [ ] **Clear, actionable feedback provided to contributor**

### Phase 4: Communication & Follow-up

#### Feedback Structure
1. **Positive Recognition**: Acknowledge good aspects first
2. **Priority Classification**: High/Medium/Low priority changes
3. **Specific Action Items**: Not just "fix documentation" but "add example for defaults_file parameter in CHEATSHEET.md"
4. **Business Context**: Explain why changes matter for users/maintainers

#### Follow-up Protocol
- **Response Timeline**: Set expectations for contributor response
- **Re-review Focus**: Only verify requested changes, don't expand scope
- **Approval Criteria**: Clear conditions for approval

### 🚨 Common Execution Failure Prevention

#### The Version Oversight Pattern
**Symptom**: Identify version issue but forget to verify fix
**Prevention**:
- Add version check to mandatory verification gates
- Never discuss version without immediately checking pyproject.toml
- Run dependency sync if version changed

#### The Documentation Analysis Gap
**Symptom**: Request documentation updates but don't verify examples work
**Prevention**:
- Test examples manually or require contributor verification
- Check that examples fit the workflow-based organization
- Verify no temporal bias introduced

#### The Test Organization Drift
**Symptom**: Accept PR-specific test naming that will age poorly
**Prevention**:
- Always consider test file names from 2+ year perspective
- Group by feature area, not implementation timeline
- Prioritize maintainer convenience over short-term convenience

## 📋 Quick Reference Templates

### Essential Review Checklist (All PRs)
```
- [ ] Tests pass: `uv run pytest tests/test_conversions.py`
- [ ] Documentation updated for user-facing changes
- [ ] No breaking changes (or migration path provided)
- [ ] Version bump appropriate (if applicable)
- [ ] Manual testing completed
```

### Bug Fix Review Template
```
**Focus Areas:**
- [ ] Root cause identified and addressed
- [ ] Test added to prevent regression
- [ ] Error handling improved
- [ ] Documentation updated if behavior changes

**Questions:**
- Does this fix the underlying issue or just symptoms?
- Could this introduce new edge cases?
- Is the fix minimal and focused?
```

### Feature PR Review Template
```
**High Priority:**
- [ ] Semantic versioning: MINOR bump for new features
- [ ] README.md: Parameter documented in Tools section
- [ ] CHEATSHEET.md: Workflow examples added
- [ ] Tests: Comprehensive coverage for new functionality
- [ ] Security: Input validation and safe practices

**Medium Priority:**
- [ ] Test organization: Feature-based naming
- [ ] Error messages: User-friendly and actionable
- [ ] Dependencies: Justified and secure
- [ ] Performance: No blocking operations

**Verification:**
- [ ] Examples in CHEATSHEET.md actually work
- [ ] No temporal bias ("NEW" markers, version annotations)
- [ ] Backward compatibility maintained
```

### Documentation Review Template
```
**Clarity:**
- [ ] Examples are copy-pasteable and work
- [ ] Organized by user workflows, not feature chronology
- [ ] Clear, actionable guidance

**Consistency:**
- [ ] No temporal bias or "new" feature distinctions
- [ ] Version references accurate
- [ ] Style matches existing documentation

**Completeness:**
- [ ] All parameters documented
- [ ] Error scenarios covered
- [ ] Real-world usage examples provided
```

### Maintenance PR Review Template
```
**Backward Compatibility:**
- [ ] Existing functionality preserved
- [ ] API changes are additive only
- [ ] Migration path for any breaking changes

**Quality:**
- [ ] Code follows existing patterns
- [ ] Dependencies updated securely
- [ ] Test coverage maintained

**Documentation:**
- [ ] Changes reflected in relevant docs
- [ ] Version changelog updated if user-facing
```

---

*This guide serves as the definitive reference for maintaining code quality, evaluating pull requests, and ensuring mcp-pandoc continues to meet MCP protocol standards while providing reliable document conversion capabilities.*
