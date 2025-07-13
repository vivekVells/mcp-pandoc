# Contributing to mcp-pandoc

Welcome! We're excited you want to contribute to mcp-pandoc. Whether you're fixing a typo, reporting a bug, or adding a major feature, this guide will help you get started.

## 🚀 Quick Start

### For Simple Contributions
**Bug fixes, documentation updates, small improvements:**

1. **Fork & clone**: Fork the repo and clone your fork
2. **Make changes**: Edit the files you need to change
3. **Test**: Run `uv run pytest tests/test_conversions.py` 
4. **Submit PR**: Create a pull request with a clear description

That's it! Our PR template will guide you through the rest.

### Development Environment

```bash
# Core dependencies
brew install pandoc uv                    # macOS
sudo apt-get install pandoc && pip install uv  # Ubuntu/Debian

# Clone and setup
git clone https://github.com/vivekVells/mcp-pandoc.git
cd mcp-pandoc
uv sync

# Verify everything works
uv run pytest tests/test_conversions.py
```

## 📝 Contribution Types

### 🐛 Bug Fixes
- Fix the issue
- Add a test if possible
- Update documentation if behavior changes

### 📚 Documentation 
- Update README.md, CHEATSHEET.md, or docstrings
- Add examples for clarity
- Fix typos or improve explanations

### 🧪 Tests
- Add tests for uncovered functionality
- Improve existing test coverage
- Fix failing tests

### ✨ New Features
**For substantial new functionality, please see [Feature Requirements](#feature-pull-request-requirements) below.**

## 💡 General Guidelines

### Code Quality
- **Follow existing patterns**: Look at `src/mcp_pandoc/server.py` for style guidance
- **Add type hints**: Include type annotations for function parameters and returns
- **Handle errors gracefully**: Provide clear, actionable error messages
- **Test your changes**: Ensure `uv run pytest tests/test_conversions.py` passes

### Security Best Practices
- Use `yaml.safe_load()` instead of `yaml.load()`
- Validate file paths with `os.path.exists()` before use
- Sanitize user inputs and provide clear error messages

### Performance Considerations
- Avoid blocking operations in async functions
- Handle large documents gracefully
- Test with various file sizes

## 🔄 Pull Request Process

1. **Create a branch**: `git checkout -b feature/description` or `git checkout -b bugfix/description`
2. **Make your changes**: Follow the guidelines above
3. **Test thoroughly**: Run the test suite and test manually
4. **Submit PR**: Use our PR template - it will guide you through the rest
5. **Respond to feedback**: Work with reviewers to refine your contribution

## 🐛 Bug Reports

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, Pandoc version)
- Relevant error messages

## ❓ Questions and Support

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and general discussion
- **Documentation**: Check README.md and CHEATSHEET.md first

## 📋 Feature Pull Request Requirements

**For substantial new features only** - simple bug fixes and documentation updates don't need this level of detail.

### Version Updates
- Follow [semantic versioning](https://semver.org/): patch for fixes, minor for features, major for breaking changes
- Update version only in `pyproject.toml` 
- Explain version bump reasoning in PR description

### Documentation Requirements
- **README.md**: Document new parameters in Tools section
- **CHEATSHEET.md**: Add practical examples for new features
- **Function docstrings**: Clear descriptions for all new functions

### Testing Requirements  
- **Comprehensive tests**: Cover new functionality and edge cases
- **Backwards compatibility**: Ensure existing functionality remains intact
- **Sustainable organization**: Use feature-based test file names, not PR-specific

### Dependencies
- **Justify new dependencies**: Clear explanation of necessity
- **Security assessment**: Ensure dependencies are secure and well-maintained
- **Version constraints**: Use appropriate pinning (e.g., `>=6.0.2`)

### Code Quality
- **Type hints**: All new functions include proper type annotations
- **Error handling**: User-friendly error messages with actionable guidance
- **Security**: Validate file paths, use `yaml.safe_load()`, sanitize inputs

---

## 🏆 Recognition

Contributors who follow these guidelines help make mcp-pandoc better for everyone. Thank you for your contributions!