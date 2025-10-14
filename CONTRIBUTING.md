# 🤝 Contributing to LinkedIn CV Generator

Thank you for your interest in contributing to the LinkedIn CV Generator! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Project Structure](#-project-structure)
- [Development Workflow](#-development-workflow)
- [Coding Standards](#-coding-standards)
- [Testing](#-testing)
- [Commit Guidelines](#-commit-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Reporting Issues](#-reporting-issues)
- [Feature Requests](#-feature-requests)

---

## 📜 Code of Conduct

By participating in this project, you agree to maintain a respectful and collaborative environment. We expect all contributors to:

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other contributors

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Poetry** for dependency management ([Install Guide](https://python-poetry.org/docs/#installation))
- **Git** for version control

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/linkedin-cv.git
   cd linkedin-cv
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/alexcolls/linkedin-cv.git
   ```

---

## 💻 Development Setup

### 1. Install Dependencies

```bash
# Install all dependencies (including dev dependencies)
poetry install

# Activate virtual environment
poetry shell

# Install Playwright browsers (if needed)
playwright install chromium
```

### 2. Configure Environment

```bash
# Copy sample environment file
cp .env.sample .env

# Edit .env with your configuration (if needed)
```

### 3. Verify Setup

```bash
# Run the interactive menu
./run.sh

# Or run tests
poetry run pytest
```

---

## 📁 Project Structure

Understanding the project structure will help you navigate the codebase:

```
linkedin-cv/
├── src/                        # Source code
│   ├── cli.py                  # CLI interface
│   ├── scraper/                # Web scraping modules
│   │   ├── linkedin_scraper.py # Browser automation
│   │   └── parser.py           # HTML parsing (core extraction logic)
│   ├── pdf/                    # PDF generation
│   │   ├── generator.py        # PDF generator
│   │   └── templates/          # HTML/CSS templates
│   └── utils/                  # Utility modules
│       ├── image_processor.py  # Image handling
│       └── extract_cookies.py  # Cookie extraction
├── tests/                      # Test suite
│   ├── test_parser.py          # Parser tests
│   └── test_pdf_generator.py   # PDF generation tests
├── docs/                       # Documentation
├── output/                     # Generated files (gitignored)
├── .session/                   # Session data (gitignored)
├── run.sh                      # Main entry point
└── pyproject.toml             # Project configuration
```

### Key Files to Know

- **`src/scraper/parser.py`** - Core extraction logic (1,260+ lines)
- **`src/pdf/templates/cv_template.html`** - CV HTML template
- **`src/pdf/templates/style.css`** - CV styling (800+ lines)
- **`run.sh`** - Interactive menu and main workflow
- **`pyproject.toml`** - Dependencies and tool configurations

---

## 🔄 Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/add-qr-code`)
- `fix/` - Bug fixes (e.g., `fix/empty-skills-section`)
- `docs/` - Documentation updates (e.g., `docs/update-readme`)
- `refactor/` - Code refactoring (e.g., `refactor/parser-methods`)
- `test/` - Test additions/updates (e.g., `test/add-parser-tests`)

### 2. Make Your Changes

- Write clean, readable code
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed
- Test your changes thoroughly

### 3. Test Your Changes

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_parser.py

# Run tests in verbose mode
poetry run pytest -v
```

### 4. Lint and Format

```bash
# Format code with black
poetry run black src/ tests/

# Sort imports with isort
poetry run isort src/ tests/

# Run linting with flake8
poetry run flake8 src/ tests/

# Type checking with mypy
poetry run mypy src/
```

### 5. Commit Your Changes

Follow the commit guidelines (see below) and commit your changes:

```bash
git add .
git commit -m "✨ Add your feature description"
```

---

## 📝 Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Formatting**: Use `black` for automatic formatting
- **Import sorting**: Use `isort` with black profile
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

### Example Code Style

```python path=null start=null
"""Module docstring explaining the purpose."""

from typing import Optional, Dict, List
from pathlib import Path


class ExampleClass:
    """Class docstring with brief description.
    
    Attributes:
        attribute_name: Description of attribute.
    """
    
    def __init__(self, name: str) -> None:
        """Initialize the class.
        
        Args:
            name: The name parameter.
        """
        self.name = name
    
    def example_method(self, param: str, optional: Optional[int] = None) -> Dict[str, str]:
        """Brief description of method.
        
        Longer description if needed.
        
        Args:
            param: Description of param.
            optional: Optional parameter description.
            
        Returns:
            Dictionary with results.
            
        Raises:
            ValueError: If param is invalid.
        """
        if not param:
            raise ValueError("param cannot be empty")
        
        return {"result": param}
```

### CSS Style Guide

For template CSS (`src/pdf/templates/style.css`):

- Use meaningful class names
- Group related styles together
- Add comments for major sections
- Use consistent spacing (4 spaces)
- Follow existing LinkedIn color scheme

### Shell Script Style

For bash scripts:

- Use `#!/usr/bin/env bash` shebang
- Add comments for complex logic
- Use absolute paths (follow project rules)
- Follow existing script patterns in `src/scripts/`

---

## 🧪 Testing

### Test Structure

Tests are organized in the `tests/` directory:

- `test_parser.py` - Tests for HTML parsing and extraction
- `test_pdf_generator.py` - Tests for PDF generation
- `test_integration.py` - End-to-end integration tests

### Writing Tests

```python path=null start=null
import pytest
from src.scraper.parser import LinkedInParser


class TestParser:
    """Test suite for LinkedInParser."""
    
    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return LinkedInParser()
    
    def test_parse_experience(self, parser):
        """Test experience parsing with valid HTML."""
        # Arrange
        html = '<div class="experience-item">...</div>'
        
        # Act
        result = parser.parse_experience(html)
        
        # Assert
        assert result is not None
        assert len(result) > 0
        assert "title" in result[0]
```

### Running Tests

```bash
# Run all tests
./run.sh  # Select option 7: Run tests

# Or directly with poetry
poetry run pytest

# With coverage report
poetry run pytest --cov=src --cov-report=html

# View coverage in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Test Coverage

We aim for **40%+ test coverage** (current project standard). New features should include tests that maintain or improve coverage.

---

## 📋 Commit Guidelines

### Commit Message Format

We use **emoji prefixes** to categorize commits:

```
<emoji> <type>: <subject>

[optional body]

[optional footer]
```

### Emoji Prefixes

| Emoji | Code | Type | Usage |
|-------|------|------|-------|
| ✨ | `:sparkles:` | Features | New features or functionality |
| 🐛 | `:bug:` | Bug Fixes | Bug fixes |
| 📚 | `:books:` | Documentation | Documentation updates |
| 🎨 | `:art:` | Styling | Code styling, formatting, CSS |
| ♻️ | `:recycle:` | Refactoring | Code refactoring without feature changes |
| 🔧 | `:wrench:` | Configuration | Configuration file changes |
| ✅ | `:white_check_mark:` | Tests | Adding or updating tests |
| 🚀 | `:rocket:` | Performance | Performance improvements |
| 🔒 | `:lock:` | Security | Security improvements |
| 🔥 | `:fire:` | Removal | Removing code or files |

### Commit Examples

```bash
# Good commit messages
git commit -m "✨ Add QR code generation for profile URL"
git commit -m "🐛 Fix empty skills section rendering"
git commit -m "📚 Update AUTHENTICATION_GUIDE with new login flow"
git commit -m "🎨 Improve CV template responsive layout"
git commit -m "♻️ Refactor parser extraction methods"
git commit -m "✅ Add tests for certification parsing"

# Bad commit messages (avoid these)
git commit -m "fix stuff"
git commit -m "updates"
git commit -m "WIP"
```

### Commit Best Practices

- **Commit by feature**: Group related changes together
- **One logical change per commit**: Don't mix unrelated changes
- **Write clear messages**: Describe what and why, not how
- **Use present tense**: "Add feature" not "Added feature"
- **Reference issues**: Include issue numbers when applicable (e.g., `Fixes #123`)

---

## 🔀 Pull Request Process

### Before Submitting

1. **Ensure all tests pass**:
   ```bash
   poetry run pytest
   ```

2. **Run code quality checks**:
   ```bash
   poetry run black src/ tests/
   poetry run flake8 src/ tests/
   poetry run mypy src/
   ```

3. **Update documentation** if needed
4. **Add tests** for new features
5. **Update CHANGELOG.md** following version guidelines

### Creating a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub

3. **Fill out the PR template** with:
   - Clear description of changes
   - Related issue numbers (if applicable)
   - Screenshots (for UI changes)
   - Testing notes

### Pull Request Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (please describe)

## Related Issues
Fixes #(issue number)

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] CHANGELOG.md updated (if applicable)
```

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be included in the next release

---

## 🐛 Reporting Issues

### Before Reporting

1. **Check existing issues** to avoid duplicates
2. **Update to the latest version** to see if the issue persists
3. **Try the troubleshooting guide**: `docs/TROUBLESHOOTING_EMPTY_DATA.md`

### Creating an Issue

Include the following information:

```markdown
## Description
Clear description of the issue.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Ubuntu 22.04, macOS 14.0]
- Python version: [e.g., 3.11.5]
- Poetry version: [e.g., 1.7.0]
- Project version: [e.g., 0.4.1]

## Additional Context
- Screenshots
- Error messages
- Logs
```

---

## 💡 Feature Requests

We welcome feature suggestions! When submitting a feature request:

1. **Use GitHub Discussions** for initial ideas
2. **Create an issue** for concrete feature proposals
3. **Include**:
   - Clear description of the feature
   - Use case and benefits
   - Proposed implementation (if you have ideas)
   - Examples or mockups (if applicable)

---

## 📚 Additional Resources

### Documentation

- [README.md](README.md) - Project overview
- [WORKFLOW.md](docs/WORKFLOW.md) - Workflow options
- [AUTHENTICATION_GUIDE.md](docs/AUTHENTICATION_GUIDE.md) - Authentication setup
- [OUTPUT_STRUCTURE.md](docs/OUTPUT_STRUCTURE.md) - Output organization
- [TROUBLESHOOTING_EMPTY_DATA.md](docs/TROUBLESHOOTING_EMPTY_DATA.md) - Debugging guide

### Tools and Libraries

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Playwright Documentation](https://playwright.dev/python/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)
- [pytest Documentation](https://docs.pytest.org/)

---

## 🎯 Development Tips

### Debugging

```bash
# Use the debug utilities
python src/utils/debug/scrape_and_save.py username

# Extract data to JSON for inspection
python src/utils/debug/extract_to_json.py username

# Check the output directory
ls -la output/username/
```

### Local Testing

```bash
# Test the full workflow
./run.sh  # Select option 1: Generate CV PDF

# Test with a specific profile
./run.sh alex-colls-outumuro
```

### Common Pitfalls

- **Import errors**: Ensure you're in the Poetry shell (`poetry shell`)
- **Test failures**: Check if Playwright browsers are installed (`playwright install`)
- **Cookie issues**: Clear `.session/` directory and re-authenticate
- **Empty data**: Review `docs/TROUBLESHOOTING_EMPTY_DATA.md`

---

## 🙏 Thank You!

Thank you for contributing to LinkedIn CV Generator! Your efforts help make this tool better for everyone.

If you have questions, feel free to:
- Open an issue
- Start a discussion on GitHub
- Reach out to the maintainers

Happy coding! 🚀

---

<p align="center">
  <b>Made with ❤️ by the LinkedIn CV Generator community</b>
</p>
