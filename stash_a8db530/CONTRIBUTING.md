# Contributing to Qyntara AI

Thank you for your interest in contributing to Qyntara AI! This document provides guidelines and instructions for contributing.

## 🎯 **Ways to Contribute**

- **Bug Reports**: Report issues via GitHub Issues
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests for bug fixes or features
- **Documentation**: Improve docs, tutorials, or examples
- **Testing**: Help test beta features and report findings
- **Community**: Answer questions, help other users

## 🚀 **Getting Started**

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/Qyntara-AI.git
cd Qyntara-AI
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,all]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📝 **Coding Standards**

### Python Style Guide

- Follow **PEP 8** (enforced via `black` and `flake8`)
- Use type hints for function signatures
- Write docstrings for all public functions/classes (Google style)
- Maximum line length: 120 characters

```python
def example_function(param: str, count: int = 0) -> bool:
    """
    Brief description of function.
    
    Args:
        param: Description of param
        count: Description of count (default: 0)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param is invalid
    """
    pass
```

### Code Quality Tools

```bash
# Format code
black qyntara_core qyntara_dcc qyntara_ai

# Check linting
flake8 qyntara_core --max-line-length=120

# Type checking
mypy qyntara_core --ignore-missing-imports
```

## ✅ **Testing**

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_core.py -v

# With coverage
pytest tests/ --cov=qyntara_core --cov-report=html
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names: `test_mesh_center_operation()`
- Include docstrings explaining what is being tested

```python
def test_mesh_center_operation():
    """Test that MeshProcessor.center_mesh() correctly centers mesh at origin"""
    # Arrange
    mesh = create_test_mesh()
    
    # Act
    centered = MeshProcessor.center_mesh(mesh)
    
    # Assert
    assert np.allclose(centered.vertices.mean(axis=0), [0, 0, 0], atol=1e-6)
```

## 📦 **Pull Request Process**

### Before Submitting

1. **Run tests**: Ensure all tests pass
2. **Add tests**: Cover new functionality with tests
3. **Update docs**: Add/update docstrings and README if needed
4. **Lint code**: Run `black` and `flake8`
5. **Commit messages**: Use clear, descriptive messages

### PR Guidelines

- **Title**: Clear, concise description (e.g., "Add FBX converter support")
- **Description**: Explain what, why, and how
  - What problem does this solve?
  - How does it work?
  - Any breaking changes?
- **Link issues**: Reference related issues (#123)
- **Screenshots**: Include before/after if UI changes

### Example PR Description

```markdown
## Description
Adds support for importing/exporting FBX files via Autodesk FBX SDK.

## Motivation
Users requested FBX support for compatibility with 3ds Max and MotionBuilder.

## Changes
- Added `fbx_converter.py` with `FBXConverter` class
- Fallback to glTF when FBX SDK not available
- Added tests in `test_fbx_converter.py`
- Updated documentation in README.md

## Breaking Changes
None

## Related Issues
Closes #42
```

## 🏗️ **Architecture Guidelines**

### Layer Structure

Respect the layered architecture:

```
qyntara_ai/        # Layer 2: AI (commercial)
    ↓
qyntara_core/      # Layer 1: Core Engine (open-source)
    ↓
qyntara_dcc/       # DCC Adapters (open-source)
```

**Rules**:
- Core Engine **MUST NOT** depend on AI layer
- DCC adapters **MAY** depend on Core Engine
- AI layer **MAY** depend on Core Engine

### File Organization

- **One class per file** (for major classes)
- Group related utilities in modules
- Use `__init__.py` to expose public API

## 🐛 **Reporting Bugs**

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Import mesh from '...'
2. Call function '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots/Error Messages**
Paste any error messages or screenshots.

**Environment**
- OS: [e.g., Windows 11, Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- Qyntara version: [e.g., 5.0.0]
- DCC: [e.g., Maya 2024]
```

## 💡 **Feature Requests**

Use GitHub Discussions or Issues to propose new features.

**Include**:
- Use case: Why is this needed?
- Proposed solution: How should it work?
- Alternatives: Any workarounds or alternatives considered?

## 📄 **License**

By contributing, you agree that your contributions will be licensed under:
- **MIT License** for Core Engine contributions
- **Commercial License** for AI Layer contributions (if applicable)

## 🙏 **Code of Conduct**

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy toward other contributors

## 📞 **Questions?**

- **GitHub Discussions**: Ask questions [here](https://github.com/Dass2023/Qyntara-AI/discussions)
- **Discord**: Join our community (coming soon)
- **Email**: dass2023@qyntara.ai

---

**Thank you for contributing to Qyntara AI!** 🚀
