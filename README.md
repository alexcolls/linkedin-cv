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

### Single Command Installation

```bash
# Clone and run - that's it!
git clone https://github.com/alexcolls/linkedin-cv.git
cd linkedin-cv
./run.sh  # Handles everything!
```

**The `run.sh` script is your ONLY entry point** - it handles:
- ✅ Dependency installation
- ✅ Authentication
- ✅ CV generation
- ✅ Testing
- ✅ Documentation
- ✅ Everything else!

### Prerequisites

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Poetry** ([Install Guide](https://python-poetry.org/docs/#installation))

### Usage (Using run.sh)

**Everything through one script:**

```bash
./run.sh  # Interactive menu with 9 options
```

#### 🔐 Method 1: Authenticated Scraping (Recommended)

Get full, unmasked content with authentication:

```bash
# Interactive (recommended)
./run.sh
# Then: 2 → Login, then 1 → Generate CV

# Or command line
./run.sh --login  # Step 1: Login
./run.sh alex-colls-outumuro  # Step 2: Generate
```

**Why authenticate?**
- ❌ Without auth: Content is masked with asterisks (`*****`)
- ✅ With auth: Full descriptions, complete profile data

**How it works:**
1. Opens Chrome browser for you to log in
2. Saves session cookies to `~/.linkedin_session.json`
3. Reuses session for ~30 days (no need to log in again!)

📚 **Full guide**: See `docs/AUTHENTICATION_GUIDE.md`

#### 🍪 Method 2: Cookie Extraction (If Chrome Already Open)

```bash
./run.sh  # Select option 3: Extract cookies
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
📋 Main Operations:
  1) 🚀 Generate CV (from URL or .env)
  2) 🔐 Login to LinkedIn (save session)
  3) 🍪 Extract cookies from Chrome

🔧 Setup & Testing:
  4) ⚙️  Run installation/setup
  5) 🧪 Run tests
  6) 📊 View test coverage

📚 Documentation:
  7) 📖 View documentation
  8) 🔍 Quick help

  9) ❌ Exit
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
│   └── utils/
│       └── image_processor.py    # Image processing
├── tests/
│   └── test_parser.py            # Comprehensive tests
├── docs/
│   ├── IMPLEMENTATION_COMPLETE.md
│   ├── IMPLEMENTATION_PROGRESS.md
│   └── HTML_EXPORT_GUIDE.md
├── scripts/
│   ├── install.sh
│   ├── test.sh
│   └── export-and-generate.sh
├── run.sh                         # Interactive menu
├── pyproject.toml
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

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Optional configuration
LINKEDIN_PROFILE_URL=https://linkedin.com/in/your-username
OUTPUT_DIR=./output
```

### Custom Templates

Create your own templates:

```bash
python src/cli.py --html profile.html --template custom_template.html
```

Template uses Jinja2 syntax with full access to profile data.

---

## 🧪 Testing

```bash
# Run all tests
./scripts/test.sh

# Or with pytest directly
pytest tests/ -v

# Check coverage
pytest tests/ --cov=src --cov-report=html
```

**Current Coverage**: 40% (comprehensive test suite with JSON-LD tests)

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

### Project Commands

```bash
# Interactive menu
./run.sh

# Installation
./scripts/install.sh

# Testing
./scripts/test.sh

# Export and generate
./scripts/export-and-generate.sh
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`pytest tests/`)
5. **Commit with emoji** (`git commit -m "✨ Add amazing feature"`)
6. **Push to branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Commit Message Convention

Use emoji prefixes:

- ✨ `:sparkles:` - New features
- 🐛 `:bug:` - Bug fixes
- 📚 `:books:` - Documentation
- 🎨 `:art:` - Styling/formatting
- ♻️ `:recycle:` - Refactoring
- 🔧 `:wrench:` - Configuration
- ✅ `:white_check_mark:` - Tests

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

## 📚 Documentation

- **[Implementation Complete](docs/IMPLEMENTATION_COMPLETE.md)** - Full feature breakdown
- **[Implementation Progress](docs/IMPLEMENTATION_PROGRESS.md)** - Development journey
- **[HTML Export Guide](docs/HTML_EXPORT_GUIDE.md)** - Step-by-step HTML export
- **[Language Guide](docs/TASK_6_LANGUAGES_GUIDE.md)** - Languages implementation

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
