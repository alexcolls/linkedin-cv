# 🎓 LinkedIn Curriculum Vitae Generator

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue?style=for-the-badge&logo=python" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/poetry-dependency%20management-blue?style=for-the-badge&logo=poetry" alt="Poetry">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/status-production%20ready-brightgreen?style=for-the-badge" alt="Production Ready">
</p>

<p align="center">
  <b>Transform your LinkedIn profile into a stunning, professional PDF CV</b><br>
  <i>With comprehensive extraction, beautiful design, and multi-page support</i>
</p>

---

## 🌟 Why LinkedIn CV Generator?

LinkedIn's built-in PDF export is **frankly terrible** - cluttered, poorly formatted, and incomplete. This tool solves that by creating **beautiful, comprehensive, professional CVs** that actually showcase your experience.

### ✨ What Makes This Special

- **🔐 🆕 Auto-Login** - First-run authentication with user consent (v0.5.2)
- **💾 Session Persistence** - Login once, use for 30 days (v0.5.2)
- **🧹 Clean HTML Output** - No LinkedIn header/sidebar clutter (v0.5.2)
- **🎨 LinkedIn-Inspired Design** - Professional styling with LinkedIn brand colors
- **📝 Complete Extraction** - ALL 11 profile sections with full descriptions
- **🖼️ Profile Photo** - Circular 120x120px with professional border
- **📧 Contact Info** - Email, phone, website in elegant cards
- **📊 Stats** - Connections and followers with badges
- **💼 Full Job Descriptions** - Multi-line text with proper formatting
- **🏆 Certifications** - With credential IDs and verification URLs
- **🌐 Languages** - With proficiency levels
- **❤️ Volunteer Work** - With causes and descriptions
- **📚 Publications** - Complete with descriptions
- **🎯 Multi-Page Support** - From 1 to 20+ pages, beautifully formatted
- **🖨️ Print-Optimized** - Perfect page breaks and print styling

---

## 📋 Complete Feature List

### Profile Sections Extracted

| Section             | Features Extracted                                                                                                                   | Visual Elements                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| **Profile Header**  | • Profile photo<br>• Name & headline<br>• Location<br>• Contact info (email, phone, website)<br>• Connection & follower stats        | • Circular photo with border<br>• Icons for all fields<br>• Stats badges<br>• Contact info grid |
| **Experience**      | • Job title & company<br>• Employment type<br>• Duration & location<br>• **Full descriptions** (multi-line)<br>• Skills used per job | • Computer icons<br>• Employment type badges<br>• Skills tags<br>• Separated cards              |
| **Education**       | • Institution & degree<br>• Field of study<br>• Duration & GPA/grade<br>• Activities & societies<br>• Descriptions                   | • School emoji<br>• Trophy for grades<br>• Activity boxes<br>• Clean hierarchy                  |
| **Skills**          | • Skill names<br>• **Endorsement counts**<br>• Category grouping                                                                     | • Thumbs up icons<br>• Blue badges<br>• 3-column grid                                           |
| **Languages**       | • Language names<br>• **Proficiency levels**<br>• All languages listed                                                               | • Globe icons<br>• Card-based layout<br>• Auto-fill grid                                        |
| **Certifications**  | • Certificate name<br>• Issuing organization<br>• Issue & expiry dates<br>• **Credential IDs**<br>• **Verification URLs**            | • Trophy icons<br>• Credential badges<br>• Date stamps<br>• Clickable URLs                      |
| **Volunteer**       | • Role & organization<br>• Duration<br>• **Cause** (e.g., Education)<br>• Full descriptions                                          | • Heart icons<br>• Cause badges<br>• Organization icons                                         |
| **Projects**        | • Project name & dates<br>• Full descriptions<br>• **Project URLs**                                                                  | • Computer icons<br>• Link icons<br>• Professional layout                                       |
| **Publications**    | • Title & publisher<br>• Publication date<br>• Descriptions                                                                          | • Document icons<br>• Italic styling<br>• Clean formatting                                      |
| **Honors & Awards** | • Award title & issuer<br>• Date received<br>• Descriptions                                                                          | • Trophy icons<br>• Green accent color<br>• Prominent display                                   |
| **Courses**         | • Course names<br>• Completion tracking                                                                                              | • Checkmark bullets<br>• List formatting                                                        |

### Design Features

#### 🎨 Professional Styling

- **LinkedIn Brand Colors** - Primary blue (#0a66c2), secondary, and accent colors
- **Typography** - Segoe UI / Helvetica Neue professional fonts
- **Consistent Spacing** - 4px/8px/16px/24px/32px spacing system
- **Icons** - 15+ emoji icons for visual enhancement
- **Badges** - Professional badges for stats, credentials, and causes

#### 📄 Layout & Structure

- **Responsive Grids** - Auto-fill and multi-column layouts
- **Card-Based Design** - Modern card components for sections
- **Section Separators** - Clear visual hierarchy
- **Flexbox Alignments** - Perfect alignment throughout
- **Multi-Page Support** - Handles 1-20+ page CVs seamlessly

#### 🖨️ Print Optimization

- **Page Break Control** - Smart breaks between sections
- **Header Protection** - Keeps headers with content
- **Orphan/Widow Prevention** - No lonely lines
- **A4 Optimization** - Perfect margins (1.5cm)
- **Print-Ready CSS** - Optimized for PDF generation

---

## 🚀 Quick Start

### Installation Options

#### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/alexcolls/linkedin-cv.git
cd linkedin-cv

# Run the installation script
./install.sh  # Interactive menu with 3 options
```

**Installation Modes:**
- **System Installation** (Recommended) - Installs globally as `linkedin-cv` command
- **Development Installation** - Local Poetry setup with `./run.sh`
- **Both** - Get both installation modes

**What the installer does:**
- ✅ Checks Python 3.9+ installation
- ✅ Installs Poetry (if needed)
- ✅ Installs system dependencies (WeasyPrint, Playwright)
- ✅ Installs Playwright browsers
- ✅ Sets up virtual environment
- ✅ Creates global command (system mode)

#### Option 2: Manual Setup

```bash
# Clone and run - that's it!
git clone https://github.com/alexcolls/linkedin-cv.git
cd linkedin-cv
./run.sh  # Handles everything!
```

**The `run.sh` script handles:**

- ✅ Dependency installation
- ✅ Authentication
- ✅ CV generation
- ✅ Testing
- ✅ Documentation
- ✅ Everything else!

### Prerequisites

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Poetry** ([Install Guide](https://python-poetry.org/docs/#installation))

### Usage

#### After System Installation

```bash
# Use from anywhere!
linkedin-cv --help
linkedin-cv https://linkedin.com/in/username
linkedin-cv alex-colls-outumuro  # Just the username!
```

#### After Development Installation (or Manual Setup)

**Everything through one script:**

```bash
./run.sh  # Interactive menu with 9 options
```

#### 🔐 Method 1: Authenticated Scraping (Recommended)

Get full, unmasked content with authentication:

```bash
# 🆕 NEW: Auto-login on first run!
./run.sh
# Then: 1 → Generate CV (login happens automatically if needed)

# Or command line
./run.sh alex-colls-outumuro  # Auto-login if not authenticated!
```

**Why authenticate?**

- ❌ Without auth: Content is masked with asterisks (`*****`)
- ✅ With auth: Full descriptions, complete profile data

**🆕 How auto-login works:**

1. **First run**: Detects no authentication → Opens browser automatically
2. **User consent**: Asks "Save session? [Y/n]" (you choose!)
3. **You log in**: Once in the browser window
4. **Session saved**: Cookies stored in `.session/linkedin_session.json` (if you said yes)
5. **Future runs**: Reuses session for ~30 days - no login needed!

**🚨 No more pre-authentication needed!** Just run and log in when prompted.

**🔒 Privacy & Control:**

- You control whether sessions are saved
- Sessions stored locally in `.session/` (not uploaded to git)
- Can opt out - just press 'n' when asked

📚 **Full guide**: See [Authentication Guide](docs/AUTHENTICATION_GUIDE.md)

#### 🍪 Method 2: Cookie Extraction (If Chrome Already Open)

```bash
./run.sh  # Select option 5: Extract cookies
```

#### 🔤 Method 3: Username Input

```bash
./run.sh username  # Just the username!
```

---

## 💻 Interactive Menu

**One script, all features:**

```bash
./run.sh
```

```
📋 Main Workflow:
  1) 📄 Generate CV PDF
  2) 📊 Extract JSON data
  3) 🌐 Extract HTML from profile

🔐 Authentication (Optional):
  4) 🔐 Pre-login to LinkedIn (manual setup)
  5) 🍪 Extract cookies from Chrome

🔧 Setup & Testing:
  6) ⚙️ Run installation/setup
  7) 🧪 Run tests
  8) 📊 View test coverage

📚 Documentation:
  9) 📖 View documentation
  h) 🔍 Quick help

  0) ❌ Exit
```

---

## 📁 Project Structure

```
linkedin-cv/
├── src/
│   ├── cli.py                    # CLI interface
│   ├── scraper/
│   │   ├── linkedin_scraper.py   # Browser automation
│   │   └── parser.py             # HTML parsing (1,260 lines!)
│   ├── pdf/
│   │   ├── generator.py          # PDF generation
│   │   └── templates/
│   │       ├── cv_template.html  # Professional template
│   │       └── style.css         # 800+ lines of styling
│   ├── utils/
│   │   ├── image_processor.py    # Image processing
│   │   ├── extract_cookies.py    # Cookie extraction utility
│   │   └── debug/               # Debug utilities
│   │       ├── scrape_and_save.py    # HTML scraping debug tool
│   │       └── extract_to_json.py    # Profile data extraction tool
│   ├── scripts/
│   │   ├── install.sh           # Old installation script
│   │   ├── common.sh            # Shared bash functions
│   │   └── export-helper.sh     # Export utilities
│   └── assets/
│       └── banner.txt           # ASCII art banner
├── docs/
│   ├── AUTHENTICATION_GUIDE.md     # Authentication documentation
│   ├── WORKFLOW.md                 # Workflow options explained
│   ├── OUTPUT_STRUCTURE.md         # Output file organization
│   └── TROUBLESHOOTING_EMPTY_DATA.md  # Debugging guide
├── output/                         # Generated CVs and data
│   └── <linkedin-username>/        # User-specific output
│       ├── profile_data.json       # Extracted profile data (option 2)
│       ├── username_*.pdf          # Generated PDF CVs (option 1)
│       └── html/                   # Raw HTML files (option 3)
├── install.sh                   # System/Dev installation script
├── uninstall.sh                 # Uninstallation script
├── run.sh                       # Interactive menu
├── pyproject.toml              # Poetry dependencies
└── README.md
```

---

## 🎨 Output Examples

### What You Get

**Header Section:**

```
┌─────────────────────────────────────────────────────┐
│  [Photo]  John Doe                                  │
│           Senior Software Engineer | San Francisco  │
│           📧 john@example.com  📞 +1-555-0123       │
│           🌐 johndoe.com                            │
│           👥 500+ connections  📊 1,200 followers   │
└─────────────────────────────────────────────────────┘
```

**Experience Section:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXPERIENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💼 Senior Software Engineer
   Acme Corp
   Full-time | 2020 - Present | San Francisco, CA

   Led development of microservices architecture
   serving 10M+ users. Implemented CI/CD pipelines
   reducing deployment time by 70%.

   Skills: Python • Docker • Kubernetes • AWS

─────────────────────────────────────────────────────
```

**Certifications:**

```
🏆 AWS Certified Solutions Architect
   Amazon Web Services
   📅 Issued: Jan 2024 | 🎟️ ID: AWS-SA-12345
   🔗 Verification: credentials.aws.com/verify/12345
```

---

## 📚 Documentation

Detailed guides available in the `docs/` directory:

| Document                                                            | Description                                                              |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| [WORKFLOW.md](docs/WORKFLOW.md)                                     | **Workflow options** - Learn about the 3 different extraction methods    |
| [AUTHENTICATION_GUIDE.md](docs/AUTHENTICATION_GUIDE.md)             | **Authentication setup** - How to log in and save sessions               |
| [OUTPUT_STRUCTURE.md](docs/OUTPUT_STRUCTURE.md)                     | **File organization** - Understanding the output directory               |
| [TROUBLESHOOTING_EMPTY_DATA.md](docs/TROUBLESHOOTING_EMPTY_DATA.md) | **Debugging guide** - Fix empty or incomplete data                       |
| [IMPLEMENTATION_COMPLETE.md](docs/IMPLEMENTATION_COMPLETE.md)       | **Architecture & features** - Complete feature breakdown                 |
| [IMPLEMENTATION_PROGRESS.md](docs/IMPLEMENTATION_PROGRESS.md)       | **Development timeline** - Detailed version history and milestones       |
| [HTML_EXPORT_GUIDE.md](docs/HTML_EXPORT_GUIDE.md)                   | **Manual HTML export** - Step-by-step guide for offline processing       |
| [TASK_6_LANGUAGES_GUIDE.md](docs/TASK_6_LANGUAGES_GUIDE.md)         | **Languages feature** - Implementation details and troubleshooting       |

### Quick Links

- **New user?** Start with [WORKFLOW.md](docs/WORKFLOW.md) to understand the options
- **Authentication issues?** Check [AUTHENTICATION_GUIDE.md](docs/AUTHENTICATION_GUIDE.md)
- **Empty data?** See [TROUBLESHOOTING_EMPTY_DATA.md](docs/TROUBLESHOOTING_EMPTY_DATA.md)
- **File structure?** Review [OUTPUT_STRUCTURE.md](docs/OUTPUT_STRUCTURE.md)

---

## 🔧 Configuration

The project uses environment variables for configuration. Copy `.env.sample` to `.env` and customize:

```bash
cp .env.sample .env
```

### Available Configuration Options

#### LinkedIn Profile

```bash
# Your LinkedIn profile URL or username
LINKEDIN_PROFILE_URL="https://www.linkedin.com/in/yourprofile/"
```

#### Output Settings

```bash
# Directory for generated PDFs and data (default: ./output)
OUTPUT_DIR="./output"

# Custom template path for PDF generation (optional)
TEMPLATE_PATH="/path/to/custom/template.html"
```

#### Logging

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
LOG_LEVEL="INFO"

# Optional: Save logs to a file
LOG_FILE="./linkedin-cv.log"
```

#### Browser Settings

```bash
# Run browser in headless mode (default: true)
HEADLESS="true"

# Browser timeout in seconds (default: 30)
BROWSER_TIMEOUT="30"

# Page load timeout in seconds (default: 60)
PAGE_LOAD_TIMEOUT="60"

# Custom user agent (optional)
USER_AGENT="Mozilla/5.0 ..."
```

#### Scraping Settings

```bash
# Pause duration between scroll actions in seconds (default: 1.5)
SCROLL_PAUSE="1.5"

# Maximum scroll attempts to load dynamic content (default: 10)
MAX_SCROLL_ATTEMPTS="10"
```

#### Session Management

```bash
# Directory for storing browser session data (optional)
SESSION_DIR="./custom_session"

# Enable session encryption for security (default: false)
ENCRYPT_SESSION="false"

# Encryption key for session data (required if ENCRYPT_SESSION=true)
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
ENCRYPTION_KEY="your-generated-key-here"
```

### Configuration Validation

The configuration system includes automatic validation with helpful error messages:

- **Type checking**: Ensures integers, floats, and booleans are valid
- **URL validation**: Verifies LinkedIn profile URLs are properly formatted
- **Path validation**: Expands home directory paths (e.g., `~/output`)
- **Log level validation**: Checks for valid logging levels

### Session Encryption

**Protect your LinkedIn session data with encryption!**

The tool supports optional encryption of stored browser sessions using Fernet symmetric encryption:

#### Generating an Encryption Key

```bash
# Using the CLI
linkedin-cv --generate-key

# Or manually
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Enabling Encryption

1. Generate a key (see above)
2. Add to your `.env` file:
   ```bash
   ENCRYPT_SESSION="true"
   ENCRYPTION_KEY="your-64-character-hex-key"
   ```
3. Your sessions are now encrypted automatically!

#### Security Features

- **Fernet symmetric encryption** with PBKDF2 key derivation
- **Automatic encryption detection** - loads both encrypted and plain sessions
- **Secure file permissions** (0o600) - only owner can read/write
- **Backward compatible** - existing plain sessions continue to work
- **Key validation** - ensures encryption keys are properly formatted

⚠️ **Important**: Keep your encryption key secure! Store it in `.env` (which is gitignored) and never commit it to version control.

### Custom Templates

Create your own PDF templates using Jinja2 syntax:

```bash
linkedin-cv https://linkedin.com/in/username --template custom_template.html
```

Templates have full access to all profile data fields.

**Test Coverage**: 88 tests passing (34% overall, 96% config, 86% encryption)

---

## 📊 Technical Highlights

### Parser Statistics

- **1,260 lines** of extraction code
- **22 extraction methods**
- **3-5 fallback selectors** per field
- **530% growth** from original

### Template & Styling

- **800+ lines** of professional CSS
- **11 complete sections** with unique styling
- **15+ emoji icons** for visual enhancement
- **60+ styled components**

### Code Quality

- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Error handling
- ✅ Modular architecture
- ✅ All tests passing

---

## 🛠️ Development

### Setup Development Environment

```bash
# Install with dev dependencies
poetry install

# Install pre-commit hooks (if available)
pre-commit install

# Run linting
poetry run black src/
poetry run flake8 src/

# Run type checking
poetry run mypy src/
```

### Installation Management

```bash
# Install (interactive)
./install.sh

# Install system-wide
./install.sh --system

# Install for development
./install.sh --dev

# Install both modes
./install.sh --both

# Uninstall (interactive)
./uninstall.sh

# Force uninstall (skip confirmations)
./uninstall.sh --force
```

### Project Commands

```bash
# Interactive menu (development mode)
./run.sh

# System command (after system installation)
linkedin-cv https://linkedin.com/in/username
```

---

## 🤝 Contributing

Contributions are welcome! We appreciate your interest in making this project better.

### Quick Start for Contributors

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`poetry run pytest`)
5. **Commit with emoji** (`git commit -m "✨ Add amazing feature"`)
6. **Push to branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### 📖 Full Contributing Guide

For detailed information about contributing, including:

- Development setup and environment configuration
- Coding standards and style guidelines
- Testing requirements and best practices
- Commit message conventions with emoji prefixes
- Pull request process and templates
- Issue reporting guidelines

**Please read our [CONTRIBUTING.md](CONTRIBUTING.md)** guide.

### Quick Emoji Reference

- ✨ `:sparkles:` - New features
- 🐛 `:bug:` - Bug fixes
- 📚 `:books:` - Documentation
- 🎨 `:art:` - Styling/formatting
- ♻️ `:recycle:` - Refactoring
- 🔧 `:wrench:` - Configuration
- ✅ `:white_check_mark:` - Tests

---

## 👤 Author

**Alex Colls Outumuro**

- 📧 Email: alexcollsoutumuro@gmail.com
- 💼 LinkedIn: [linkedin.com/in/alex-colls-outumuro](https://linkedin.com/in/alex-colls-outumuro)
- 🐙 GitHub: [@alexcolls](https://github.com/alexcolls)

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **BeautifulSoup4** - HTML parsing
- **WeasyPrint** - PDF generation
- **Playwright** - Browser automation
- **Jinja2** - Template rendering
- **Poetry** - Dependency management

---

## 📚 Additional Documentation

- **[Implementation Complete](docs/IMPLEMENTATION_COMPLETE.md)** - Comprehensive feature breakdown with architecture details
- **[Implementation Progress](docs/IMPLEMENTATION_PROGRESS.md)** - Development journey from v0.1.0 to v0.5.2
- **[HTML Export Guide](docs/HTML_EXPORT_GUIDE.md)** - Step-by-step manual HTML export for troubleshooting
- **[Languages Guide](docs/TASK_6_LANGUAGES_GUIDE.md)** - Languages feature implementation and usage

---

## ❓ FAQ

### Q: Why is my PDF empty?

**A:** LinkedIn requires authentication. Use the `--html` option with manually saved HTML instead of direct scraping.

### Q: Can I customize the design?

**A:** Yes! Edit `src/pdf/templates/cv_template.html` and `style.css` to your liking.

### Q: Does it work with all LinkedIn profiles?

**A:** Yes, it extracts whatever sections are present on the profile. Empty sections are automatically hidden.

### Q: Is it safe?

**A:** Absolutely. All processing happens locally on your machine. No data is sent anywhere.

### Q: Can I use it for my clients/company?

**A:** Yes! MIT license allows commercial use. Check LICENSE for details.

---

## 🚀 Roadmap

### Future Enhancements

- [ ] Multi-language PDF support
- [ ] Custom color themes
- [ ] QR code for profile URL
- [ ] Export to Word/HTML formats
- [ ] Batch processing multiple profiles
- [ ] Cloud deployment option
- [ ] API endpoint

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/alexcolls/linkedin-cv/issues)
- **Discussions**: [GitHub Discussions](https://github.com/alexcolls/linkedin-cv/discussions)

---

## ⭐ Show Your Support

If this project helped you, please consider:

- ⭐ **Starring the repository**
- 🐛 **Reporting bugs**
- 💡 **Suggesting features**
- 🤝 **Contributing code**
- 📢 **Sharing with others**

---

<p align="center">
  <b>Made with ❤️ and 🐍 Python</b><br>
  <i>Transform your LinkedIn profile into a masterpiece Curriculum Vitae</i>
</p>

<p align="center">
  <sub>© 2024 LinkedIn CV Generator | MIT License</sub>
</p>
