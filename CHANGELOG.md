# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2025-10-12

### Added
- 🎨 **ASCII Banner** - Beautiful ASCII art banner from assets/banner.txt displayed in main menu
- 📁 **User-Specific Output** - Output files now organized in `output/<linkedin-username>/` directories
- 🛠️ **Debug Utilities** - Moved debug scripts to `src/utils/debug/` for better organization

### Changed
- 🗂️ **Project Reorganization** - Cleaner structure with all Python files properly placed
- 📝 **Output Structure** - JSON saved as `profile_data.json`, PDFs as `cv_<timestamp>.pdf` per user
- 🚀 **Menu Enhanced** - Improved visual presentation with ASCII banner
- 📋 **Scripts Consolidated** - Removed test.sh, keeping only essential scripts

### Fixed
- 🐛 **Banner Display** - Now reads from external file instead of inline ASCII
- 🔧 **File Organization** - All utility scripts properly categorized

### Removed
- 🧪 **Test Files** - Temporarily removed tests directory for complete rewrite later
- 📊 **Test Coverage** - Removed coverage-related files (.coverage, .pytest_cache)

## [0.4.0] - 2025-10-09

### Added
- 🔐 **LinkedIn Authentication System** - Interactive login with persistent session cookies
- 🍪 **Cookie Extraction Script** - Extract cookies from running Chrome browser (`scripts/extract_cookies.py`)
- 📊 **JSON-LD Parser** - Parse LinkedIn's structured data for public profiles
- ✨ **Username Normalization** - Accept just username instead of full URL (e.g., "alex-colls-outumuro")
- 🌐 **Chrome Profile Integration** - Attempt to use existing Chrome session automatically
- 📚 **Authentication Guide** - Comprehensive documentation in `docs/AUTHENTICATION_GUIDE.md`
- 🔐 **Login Command** - New `--login` flag for interactive authentication
- 💻 **Interactive Menu Enhanced** - Added "Login to LinkedIn" option in run.sh
- 🧪 **JSON-LD Tests** - Comprehensive test suite for structured data parsing
- 🎯 **Auth Wall Detection** - Smart detection of LinkedIn authentication requirements

### Changed
- ⬆️ **Test Coverage** - Improved from 21% to 40% (almost doubled!)
- 🔧 **CLI Enhanced** - Now prompts for profile URL if not provided
- 📝 **README Updated** - Added authentication instructions and workflow
- 🎨 **Menu Simplified** - Removed HTML file options from interactive menu
- ⚡ **Parser Improved** - Falls back to HTML scraping if JSON-LD not available

### Fixed
- 🐛 **Content Masking** - Solved asterisk (`*****`) issue with proper authentication
- 🔒 **Auth Wall** - Proper session management for authenticated scraping
- ✅ **All Tests** - Fixed failing e2e and CLI tests
- 🌐 **Chrome Integration** - Handle locked profile directory gracefully

## [0.3.0] - 2025-10-04

### Added
- 📜 **--html-file option** - Generate PDFs from manually saved LinkedIn HTML files
- 📖 **HTML_EXPORT_GUIDE.md** - Comprehensive guide for exporting LinkedIn profile HTML
- ⚠️ **LinkedIn authentication warning** - Documentation about authentication wall issues

### Changed
- ⬆️ **WeasyPrint updated** - Upgraded from v60.0 to v62.x to fix pydyf compatibility
- 📄 **CLI improved** - PROFILE_URL argument now optional when using --html-file
- 📝 **Documentation enhanced** - README updated with HTML file workflow

### Fixed
- 🐛 **WeasyPrint PDF generation** - Fixed `PDF.__init__()` compatibility issue with pydyf
- 🔒 **Authentication wall handling** - Added workaround for LinkedIn login requirements

## [0.2.0] - 2025-10-04

### Added
- 🚀 **install.sh** - One-command installation script with system detection
- 🚀 **run.sh** - Quick run script with automatic dependency checking
- 🧪 **test.sh** - Comprehensive test runner with coverage and code quality checks
- 🐳 **Dockerfile** - Production-ready containerization with multi-stage build
- ✅ **Complete E2E test suite** - End-to-end workflow testing
- ✅ **CLI integration tests** - Full CLI command testing
- ✅ **Enhanced unit tests** - Comprehensive test coverage for all components
- 📦 **.dockerignore** - Optimized Docker build context

### Improved
- 🧪 Test coverage increased significantly
- 📝 Better developer experience with helper scripts
- 🐳 Easy deployment with Docker support
- 🔧 Automated setup and testing workflows

## [0.1.0] - 2025-10-04

### Added
- 🎉 Initial release of LinkedIn CV Generator
- 🔍 LinkedIn profile scraping with Playwright browser automation
- 📄 PDF generation using WeasyPrint for high-quality output
- 📸 Profile picture downloading and embedding
- 🎨 Beautiful HTML/CSS templates with LinkedIn-inspired design
- 💻 Command-line interface with Click
- 📋 Support for all LinkedIn profile sections:
  - Profile header (name, headline, location, contact)
  - About/Summary
  - Experience (work history)
  - Education
  - Skills
  - Certifications
  - Languages
  - Volunteer Experience
  - Projects
  - Publications
  - Honors & Awards
  - Courses
- 🛠️ Customizable HTML/CSS templates
- ⚙️ Configurable CLI options (output directory, template, headless mode, debug)
- 🎯 Smart file naming with username and timestamp
- 🧪 Basic test suite with pytest
- 📖 Comprehensive documentation and README
- 🔒 Privacy-focused design (local processing only)
- 🎨 Rich terminal output with progress indicators
- ⚡ Async scraping for better performance
- 🔧 Development tools integration (Black, Flake8, MyPy, isort, pre-commit)

[Unreleased]: https://github.com/alexcolls/linkedin-cv/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/alexcolls/linkedin-cv/releases/tag/v0.1.0
