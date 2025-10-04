# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
