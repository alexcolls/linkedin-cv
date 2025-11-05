# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2025-11-05

### Added
- 🎨 **Beautiful PDF Template System** - Major redesign with 4 professional themes
  * **Modern Professional**: Two-column layout with gradient header, Inter/Poppins fonts, timeline visualization, progress bars for skills
  * **Creative Bold**: Asymmetric three-column design, vibrant purple/pink/green colors, Montserrat/Raleway fonts, organic shape borders
  * **Executive Elegant**: Traditional single-column layout, Playfair Display/Source Serif Pro serif fonts, navy/burgundy/gold colors, refined spacing
  * **Classic**: Original LinkedIn-inspired design (preserved for backwards compatibility)
- 🎨 **Template Manager Architecture** - Centralized template system with theme selection and customization
  * `TemplateManager` class for rendering templates with color schemes
  * `ColorScheme` dataclass for customizable color palettes
  * Theme validation and error handling
- 🎨 **CLI Theme Options** - New command-line flags for template customization
  * `--theme {modern|creative|executive|classic}` - Select CV template theme (default: modern)
  * `--list-themes` - Display all available themes with descriptions
  * `--color-primary #HEX` - Override primary color
  * `--color-accent #HEX` - Override accent color
- 🚀 **QR Code Generation** - Generate QR codes for LinkedIn profile URLs
  * `QRGenerator` utility class with customizable styling
  * Support for QR codes with optional logo overlay
  * Base64 data URI output for embedding in PDFs
  * High error correction for logo placement
- ✅ **Comprehensive Test Suite** - 20 new tests for template system
  * Tests for all 4 themes and color schemes
  * Template rendering with various profile data
  * Integration tests for full profiles
  * 96% coverage for template manager module
  * Total: 108 tests passing (up from 88)
- 📊 **Development Tracker** - DEVELOPMENT_STATUS.md documenting progress and roadmap

### Changed
- 🏗️ **Template Directory Structure** - Reorganized into theme-based subdirectories
  * `src/pdf/templates/modern/` - Modern Professional theme
  * `src/pdf/templates/creative/` - Creative Bold theme
  * `src/pdf/templates/executive/` - Executive Elegant theme
  * `src/pdf/templates/classic/` - Classic theme (original)
- 🔧 **PDF Generator Enhanced** - Updated to use TemplateManager
  * Support for theme parameter in constructor
  * Custom color scheme support
  * Improved error messages with context
  * Theme validation before rendering
- 📝 **CLI Workflow Updated** - Theme selection integrated throughout
  * Progress messages show selected theme
  * Theme validation and helpful error messages
  * Color customization passed through entire workflow
- ⬆️ **Dependencies Added** - New libraries for enhanced features
  * `qrcode` v8.2 - QR code generation
- 📈 **Test Coverage** - Improved from 37% to 38% overall
  * Template manager: 96% coverage
  * Config module: 95% coverage
  * Encryption module: 86% coverage

### Improved
- 🎨 **Visual Design** - Professional, modern, and elegant CV templates
  * Modern gradient headers and timeline visualizations
  * Creative asymmetric layouts with vibrant colors
  * Executive traditional design with refined typography
  * All templates print-optimized for A4 paper
- 🚀 **User Experience** - Easy theme selection and customization
  * Interactive theme list command
  * Simple color overrides via CLI
  * Clear progress indicators during generation
- 📚 **Code Quality** - Well-tested and documented template system
  * Comprehensive test coverage for new features
  * Type hints throughout template manager
  * Clear separation of concerns

### Technical Details
- **Modern Template**: 634 lines CSS, two-column with sidebar, gradient/shadow effects
- **Creative Template**: 534 lines CSS, three-column asymmetric, bold typography
- **Executive Template**: 400 lines CSS, single-column centered, serif fonts
- **Template Manager**: 241 lines, 80 statements, 96% test coverage
- **QR Generator**: 124 lines with PIL/qrcode integration
- **New Tests**: 267 lines, 20 test cases, all passing

## [0.4.2] - 2025-10-14

### Added
- 📦 **System/Development Installation Scripts** - Professional install.sh and uninstall.sh
  * Interactive installation with 3 modes: System, Development, or Both
  * System installation: Global `linkedin-cv` command in ~/.local/bin
  * Development installation: Local Poetry environment with ./run.sh
  * Automatic dependency detection (Python 3.9+, Poetry)
  * System dependencies installation (WeasyPrint, Playwright libraries)
  * Playwright browser installation (Chromium with deps)
  * Installation markers for tracking installed modes
- 🗑️ **Clean Uninstallation** - Comprehensive uninstall.sh script
  * Removes system and/or development installations
  * Optional cleanup of .env, output/, and data/ directories
  * Force mode with --force flag
  * Safe defaults with user confirmations
  * Poetry virtual environment cleanup
- 🎨 **Beautiful Terminal Output** - Colorful installation progress
  * Progress indicators with emojis
  * Clear status messages
  * Success/warning/error visual feedback
  * Installation summary at completion

### Changed
- 📚 **README Enhanced** - Added installation section with both automated and manual options
- 📁 **Project Structure** - Added install.sh and uninstall.sh to root directory
- 🔧 **Installation Process** - Now offers both global and local installation modes

### Improved
- 🚀 **User Experience** - One-command installation for easy setup
- 🧹 **Cleanup Process** - Safe uninstallation with data preservation options
- 📖 **Documentation** - Clear installation and usage instructions

## [0.5.2] - 2025-10-12

### Added
- 🤝 **User Consent for Session Storage** - First-time login now asks: "Save session? [Y/n]"
  * Clear explanation of what's stored and duration
  * Users can opt out of session persistence
  * Better transparency and user control
- 📁 **Project-Local Session Storage** - Sessions stored in `.session/` directory
  * Moved from `~/.linkedin_session.json` to `.session/linkedin_session.json`
  * Cleaner, more predictable location
  * Auto-created on first use

### Fixed
- 🐛 **Session Persistence Bug** - Sessions now save correctly after login!
  * Problem: Session not being saved → asked to login every time
  * Solution: Proper session save/load flow implemented
  * Sessions now persist for full 30 days as intended
- 🎨 **Clean Index.html** - Removed LinkedIn header and right sidebar
  * No navigation bar clutter
  * No language selector or settings panel
  * Full-width main content for better readability
  * Professional, focused profile view

### Changed
- 📂 **Session File Location** - `.session/linkedin_session.json` (project-local)
- 🔒 **Security** - Added `.session/` to `.gitignore`
- 📚 **Documentation** - Updated all session path references

### Improved
- ✅ Session persistence now works reliably
- 🎯 Better user experience with consent prompt
- 🧹 Cleaner HTML output without LinkedIn UI elements

## [0.5.1] - 2025-10-12

### Added
- 🔐 **Auto-Login on First Run** - No more pre-authentication needed!
  * Automatically detects missing/invalid LinkedIn authentication
  * Opens browser for login only when needed
  * Works with all main workflow options (1, 2, 3)
- ✅ **Smart Authentication Check** - Validates `li_at` cookie presence
- 🎯 **Seamless User Experience** - Just run, log in when prompted, done!

### Changed
- 📋 **Menu Updated** - Options 1-3 now show "(auto-login if needed)" hint
- 📚 **Documentation** - Updated README and run.sh help with auto-login info
- 🔐 **Authentication Section** - Changed from required to "Optional" in menu
- ℹ️ **Quick Start Guide** - Simplified from 3 steps to 2 steps

### Improved
- 🚀 **Developer Experience** - No need to remember to login first
- 📖 **User Guidance** - Clear messages when authentication is needed
- 🎨 **Menu Clarity** - Better indication of which options auto-authenticate

## [0.5.0] - 2025-10-12

### Added
- 🌐 **Multi-Page Scraping** - New `scrape_all_sections()` method extracts data from dedicated LinkedIn detail pages
- 📁 **Complete HTML Extraction** - Scrapes 10+ detail pages: experience, education, skills, certifications, projects, languages, volunteer, honors, publications
- 🛠️ **Three Workflow Options**:
  * Option 1: Generate CV PDF (all-in-one, recommended)
  * Option 2: Extract JSON data (with automatic HTML cleanup)
  * Option 3: Extract HTML from profile (advanced debugging)
- 🧹 **Automatic Cleanup** - Option 2 removes HTML files after JSON extraction
- 💾 **HTML Debug Files** - Each section saved as `last_scraped_<section>.html` for debugging
- 📊 **Metadata Tracking** - Timestamps and URLs tracked in metadata.json
- 📝 **Enhanced Parsers** - New methods: `parse_experience_detail()`, `parse_education_detail()`, `parse_skills_detail()`
- 📚 **Comprehensive Documentation**:
  * WORKFLOW.md - Detailed workflow options guide
  * OUTPUT_STRUCTURE.md - File organization reference
  * TROUBLESHOOTING_EMPTY_DATA.md - Debugging guide
  * All docs linked from README

### Changed
- 🔄 **Menu Reordered** - Simplified: 1) Generate PDF, 2) Extract JSON, 3) Extract HTML
- 📝 **PDF Naming** - Changed from `cv_timestamp.pdf` to `username_timestamp.pdf`
- 📂 **File Structure** - HTML files now in `output/<username>/html/` subdirectory
- 🔢 **Menu References** - Updated all option numbers (Login=4, Cookies=5, etc.)
- 📚 **Documentation** - README now includes quick links to all documentation
- 🏇 **Workflow Description** - Removed "(in order)" text, clarified each option's purpose

### Fixed
- ✅ **Experience Extraction** - Fixed to process only main UL, not nested ones (37 → 5 correct items)
- ✅ **About Section** - Fixed extraction using anchor div parent lookup
- ✅ **Grouped Experience** - Properly handles nested roles under company entries

## [0.4.1] - 2025-10-12

### Added
- 🎨 **ASCII Banner** - Beautiful ASCII art banner from src/assets/banner.txt displayed in main menu
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
- 🍪 **Cookie Extraction Script** - Extract cookies from running Chrome browser (`src/utils/extract_cookies.py`)
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
