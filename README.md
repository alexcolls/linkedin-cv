# 🖨️ LinkedIn Beatiful & Complete Profile CV Downloader

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/poetry-dependency%20management-blue?style=flat-square" alt="Poetry">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License">
  <img src="https://img.shields.io/badge/code%20style-black-black?style=flat-square" alt="Code style: black">
  <img src="https://img.shields.io/badge/browser-playwright-green?style=flat-square" alt="Playwright">
</p>

<p align="center">
  <b>Generate beautiful, professional PDF CVs from LinkedIn profiles</b>
</p>

---

## 🎯 Overview

**LinkedIn CV Generator** is an open-source Python tool that scrapes your LinkedIn profile and generates a **beautifully designed PDF CV** with all your professional information. Unlike LinkedIn's native PDF export (which is frankly terrible), this tool creates a polished, professional-looking document that actually looks good.

### Why This Tool?

LinkedIn's built-in "Save to PDF" feature produces poorly formatted, cluttered documents that don't do justice to your professional profile. This tool solves that problem by:

- 🎨 **Beautiful Design** - Clean, modern layout inspired by LinkedIn's visual style but significantly improved
- 📋 **Complete Profile** - Captures ALL sections: summary, experience, education, skills, certifications, projects, and more
- 📸 **Profile Picture** - Embeds your profile photo in high quality
- 🎯 **Professional Output** - Ready for job applications, networking, and portfolio use
- 🔓 **Open Source** - MIT licensed, customize as you wish
- 🚀 **Fast & Local** - All processing happens on your machine, no data leaves your computer

## ✨ Features

- ✅ **Automated LinkedIn Scraping** - Uses Playwright for reliable, modern browser automation
- ✅ **All Profile Sections** - Experience, education, skills, certifications, languages, volunteer work, projects, publications
- ✅ **High-Quality PDF** - WeasyPrint generates pixel-perfect PDFs from HTML/CSS templates
- ✅ **Profile Picture Embedding** - Downloads and embeds your LinkedIn profile photo
- ✅ **Smart Formatting** - Automatically formats dates, locations, and descriptions
- ✅ **Clean CLI** - Simple command-line interface with clear messages and progress indicators
- ✅ **Customizable Templates** - Easily modify HTML/CSS templates to match your style
- ✅ **Timestamp Naming** - Output files named as `<username>_<timestamp>.pdf` for version control
- ✅ **No Configuration Needed** - Just run it on your LinkedIn profile URL

## 📁 Project Structure

```
linkedin-cv/
├── pyproject.toml              # Poetry dependencies and project configuration
├── poetry.lock                 # Locked dependency versions
├── README.md                   # This file
├── LICENSE                     # MIT License
├── CHANGELOG.md                # Version history and release notes
├── .gitignore                  # Git ignore patterns
├── src/
│   ├── __init__.py             # Package initialization
│   ├── cli.py                  # Command-line interface entry point
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── linkedin_scraper.py # Main scraping logic with Playwright
│   │   └── parser.py           # HTML parsing and data extraction
│   ├── pdf/
│   │   ├── __init__.py
│   │   ├── generator.py        # PDF generation with WeasyPrint
│   │   └── templates/
│   │       ├── style.css       # LinkedIn-inspired CSS styling
│   │       └── cv_template.html # HTML template for PDF layout
│   └── utils/
│       ├── __init__.py
│       └── image_processor.py  # Profile picture processing
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py         # Scraper unit tests
│   ├── test_pdf_generator.py  # PDF generation tests
│   └── fixtures/               # Test data and mock responses
├── output/                      # Generated PDF files (gitignored)
└── assets/
    ├── banner.txt              # ASCII art banner
    └── example_output.png      # Example PDF screenshot
```

### Component Responsibilities

- **`cli.py`** - Entry point with argument parsing, ASCII banner, user prompts, and flow control
- **`scraper/linkedin_scraper.py`** - Playwright automation to navigate LinkedIn and extract HTML
- **`scraper/parser.py`** - BeautifulSoup parsing to extract structured data from LinkedIn's HTML
- **`pdf/generator.py`** - Orchestrates HTML template rendering and WeasyPrint PDF generation
- **`pdf/templates/`** - HTML/CSS templates for professional CV layout
- **`utils/image_processor.py`** - Downloads, processes, and embeds profile pictures

## 🚀 Installation

### Prerequisites

- **Python 3.9+** - Modern Python version required
- **Poetry** - Dependency management ([install guide](https://python-poetry.org/docs/#installation))
- **Linux/macOS** - Primary support (Windows should work but untested)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/alexcolls/linkedin-cv.git
cd linkedin-cv

# 2. Install dependencies with Poetry
poetry install

# 3. Install Playwright browsers (required for scraping)
poetry run playwright install chromium

# 4. Run the tool
poetry run python -m src.cli https://www.linkedin.com/in/your-username/
```

**Note:** No `.env` configuration needed! This is a personal-use tool designed for simplicity.

## 💻 Usage

### Basic Command

```bash
poetry run python -m src.cli <linkedin-profile-url>
```

### Command-Line Options

```bash
poetry run python -m src.cli [OPTIONS] <linkedin-profile-url>

Options:
  -o, --output-dir PATH    Output directory for generated PDFs [default: ./output]
  -t, --template PATH      Custom HTML template path [default: built-in]
  --headless / --no-headless  Run browser in headless mode [default: headless]
  --debug                  Enable debug logging
  --help                   Show this message and exit
```

### Examples

```bash
# Basic usage - generates PDF in ./output/
poetry run python -m src.cli https://www.linkedin.com/in/johndoe/

# Custom output directory
poetry run python -m src.cli -o ~/Documents/CVs https://www.linkedin.com/in/johndoe/

# Debug mode with visible browser
poetry run python -m src.cli --no-headless --debug https://www.linkedin.com/in/johndoe/

# Custom template
poetry run python -m src.cli -t my_custom_template.html https://www.linkedin.com/in/johndoe/
```

### Output

Generated PDFs are named with the format:
```
<linkedin-username>_<timestamp>.pdf
```

Example:
```
john-doe_2025-10-04-032234.pdf
```

### CLI Flow

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██╗     ██╗███╗   ██╗██╗  ██╗███████╗██████╗ ██╗███╗   ██╗║
║   ██║     ██║████╗  ██║██║ ██╔╝██╔════╝██╔══██╗██║████╗  ██║║
║   ██║     ██║██╔██╗ ██║█████╔╝ █████╗  ██║  ██║██║██╔██╗ ██║║
║   ██║     ██║██║╚██╗██║██╔═██╗ ██╔══╝  ██║  ██║██║██║╚██╗██║║
║   ███████╗██║██║ ╚████║██║  ██╗███████╗██████╔╝██║██║ ╚████║║
║   ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝╚═╝  ╚═══╝║
║                                                              ║
║              📄 Professional CV Generator 📄                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🔍 Scraping LinkedIn profile...
   → Launching browser...
   → Navigating to profile...
   → Extracting profile data...
   → Parsing 8 sections...
   ✓ Profile scraped successfully!

📸 Processing profile picture...
   → Downloading image...
   → Optimizing quality...
   ✓ Profile picture ready!

📄 Generating PDF...
   → Rendering HTML template...
   → Applying LinkedIn-inspired styling...
   → Converting to PDF with WeasyPrint...
   ✓ PDF generated successfully!

✅ Done! Your CV is ready at:
   output/john-doe_2025-10-04-032234.pdf
```

## 🛠️ Dependencies

### Runtime Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `playwright` | ^1.40.0 | Modern browser automation for LinkedIn scraping |
| `beautifulsoup4` | ^4.12.0 | HTML parsing and data extraction |
| `lxml` | ^5.0.0 | XML/HTML parser for BeautifulSoup |
| `weasyprint` | ^60.0 | High-quality HTML/CSS to PDF conversion |
| `pillow` | ^10.0.0 | Image processing and optimization |
| `click` | ^8.1.0 | CLI argument parsing and commands |
| `rich` | ^13.0.0 | Beautiful terminal output and progress bars |
| `requests` | ^2.31.0 | HTTP requests for image downloads |
| `jinja2` | ^3.1.0 | Template rendering for HTML generation |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | ^7.4.0 | Testing framework |
| `pytest-cov` | ^4.1.0 | Coverage reporting |
| `pytest-mock` | ^3.12.0 | Mocking support |
| `black` | ^23.12.0 | Code formatting |
| `flake8` | ^6.1.0 | Code linting |
| `mypy` | ^1.7.0 | Static type checking |
| `isort` | ^5.13.0 | Import sorting |
| `pre-commit` | ^3.5.0 | Git pre-commit hooks |

## 🎨 PDF Design & Templates

### Template Structure

The PDF is generated from HTML/CSS templates that capture LinkedIn's visual appeal while improving readability and print quality.

**Template Location:** `src/pdf/templates/`

```
templates/
├── cv_template.html    # Main HTML structure
└── style.css           # LinkedIn-inspired styling
```

### Included Sections

The generated PDF includes all available LinkedIn sections:

1. **Header** - Name, headline, location, contact info
2. **Profile Picture** - High-resolution photo (if available)
3. **About/Summary** - Professional summary/bio
4. **Experience** - Work history with dates, titles, companies, descriptions
5. **Education** - Degrees, institutions, dates, fields of study
6. **Skills** - Endorsements and skill categories
7. **Certifications** - Professional certifications with issuing organizations
8. **Languages** - Language proficiencies
9. **Volunteer Experience** - Volunteer work and causes
10. **Projects** - Portfolio projects with descriptions
11. **Publications** - Research papers, articles, books
12. **Honors & Awards** - Recognition and achievements
13. **Courses** - Completed courses and training

### Customization

You can customize the template by editing the HTML/CSS files:

```css
/* src/pdf/templates/style.css */

:root {
  --primary-color: #0a66c2;        /* LinkedIn blue */
  --secondary-color: #70b5f9;
  --text-color: #000000;
  --text-muted: #666666;
  --background: #ffffff;
  --border-color: #e0e0e0;
  --font-family: 'Segoe UI', Tahoma, sans-serif;
}

/* Customize as needed */
```

**Using Custom Templates:**
```bash
poetry run python -m src.cli -t /absolute/path/to/my_template.html <profile-url>
```

### Design Features

- ✅ **Clean Typography** - Professional fonts with proper hierarchy
- ✅ **LinkedIn Colors** - Familiar color palette with better contrast
- ✅ **Responsive Layout** - Optimized for A4/Letter paper sizes
- ✅ **Print-Friendly** - High-quality output suitable for printing
- ✅ **Section Dividers** - Clear visual separation between sections
- ✅ **Icon Integration** - Optional icons for visual appeal (via Unicode)
- ✅ **Multi-Page Support** - Handles profiles of any length

## 🧪 Development

### Setup Development Environment

```bash
# Clone and install
git clone https://github.com/alexcolls/linkedin-cv.git
cd linkedin-cv
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Activate Poetry shell
poetry shell
```

### Code Quality Tools

```bash
# Format code with Black
poetry run black src/ tests/

# Sort imports
poetry run isort src/ tests/

# Lint code with Flake8
poetry run flake8 src/ tests/

# Type check with MyPy
poetry run mypy src/

# Run all quality checks
poetry run pre-commit run --all-files
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_scraper.py

# Run with verbose output
poetry run pytest -v

# Run in watch mode (requires pytest-watch)
poetry run ptw
```

### Project Structure for Development

```python
# src/scraper/linkedin_scraper.py
class LinkedInScraper:
    """Handles LinkedIn profile scraping with Playwright."""
    
    async def scrape_profile(self, profile_url: str) -> dict:
        """Main scraping method."""
        pass

# src/pdf/generator.py
class PDFGenerator:
    """Generates PDF from profile data."""
    
    def generate(self, profile_data: dict, output_path: str) -> None:
        """Main PDF generation method."""
        pass
```

## ⚠️ Legal & Ethical Considerations

### Legal Notice

**IMPORTANT:** This tool is designed for **personal use only** to generate CVs from your own LinkedIn profile.

- ✅ **Acceptable Use:** Scraping your own profile for personal CV generation
- ❌ **Unacceptable Use:** Bulk scraping, data collection, scraping other people's profiles

**LinkedIn's Terms of Service:** Be aware that automated scraping may violate LinkedIn's Terms of Service. Use responsibly and at your own risk.

### 🔒 Security & Privacy

- ✅ **Local Processing** - All data processing happens on your machine
- ✅ **No Data Storage** - Profile data is not stored or transmitted
- ✅ **No Credentials Stored** - No passwords or API keys required/stored
- ✅ **Open Source** - Full transparency, audit the code yourself

### 🤝 Ethical Use Guidelines

1. **Personal Use Only** - Use this tool only for your own profile
2. **Respect Rate Limits** - Don't make excessive requests to LinkedIn
3. **No Automation at Scale** - Not intended for bulk processing
4. **Keep It Local** - Don't build services on top of this tool
5. **Be Transparent** - If using the generated CV, you can mention it's self-generated

### Disclaimer

The authors and contributors of this project:
- Provide this software "as is" without warranty of any kind
- Are not responsible for how you use this tool
- Do not endorse any violation of LinkedIn's Terms of Service
- Assume no liability for any consequences of using this software

**Use responsibly and at your own risk.**

## 🎯 Use Cases

### Perfect For

- 📄 **Job Applications** - Professional CVs for application portals
- 💼 **Portfolio Building** - Beautiful resumes for your portfolio site
- 🗄️ **Offline Backup** - Keep an up-to-date copy of your profile
- 📧 **Email Attachments** - Send polished CVs to recruiters
- 🖨️ **Print Quality** - High-quality PDFs for networking events
- 📱 **Quick Updates** - Regenerate CV whenever you update LinkedIn
- 🎨 **Custom Branding** - Modify templates to match personal brand

### Real-World Scenarios

1. **Last-Minute Applications** - Need a CV now? Generate it in 30 seconds
2. **Multiple Versions** - Create dated versions to track career progression
3. **No Design Skills** - Get professional results without design experience
4. **Consistent Format** - Same structure as your well-maintained LinkedIn
5. **ATS-Friendly** - Clean text structure works well with applicant tracking systems

## 🗺️ Roadmap

### Current Version: v0.1.0

### Planned Features

- [ ] **Multiple Template Styles** - Classic, Modern, Minimal, Creative designs
- [ ] **Language Support** - Generate CVs in multiple languages
- [ ] **Section Filtering** - Choose which sections to include
- [ ] **Export Formats** - Support for DOCX, HTML, Markdown in addition to PDF
- [ ] **Comparison View** - Side-by-side comparison of profile versions
- [ ] **Headless API Mode** - Use as a library in other projects
- [ ] **Configuration File** - Optional YAML config for preferences
- [ ] **Interactive Template Builder** - GUI for template customization
- [ ] **Resume Optimization** - AI-powered suggestions for improvement
- [ ] **Batch Processing** - Process multiple profiles (with proper auth)

### Future Enhancements

- 🎨 Template gallery with downloadable designs
- 📊 Analytics on profile completeness
- 🔄 Auto-regeneration on LinkedIn updates (via webhooks)
- 🌍 Multi-language profile support
- 📱 Mobile-responsive HTML output
- 🎯 Job-specific CV tailoring

**Want to contribute?** See the [Contributing](#-contributing) section below!

## 🐛 Troubleshooting

### Common Issues

#### 1. Playwright Browser Not Found

**Error:** `Browser executable not found`

**Solution:**
```bash
poetry run playwright install chromium
```

#### 2. LinkedIn Login Required

**Error:** `Cannot access profile (login required)`

**Solution:**
- LinkedIn may require authentication for some profiles
- Run with `--no-headless` flag and manually log in
- Consider using your own profile URL (while logged in)

#### 3. WeasyPrint Installation Errors

**Error:** `Failed to load libcairo` or similar

**Solution (Ubuntu/Debian):**
```bash
sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**Solution (macOS):**
```bash
brew install cairo pango gdk-pixbuf libffi
```

#### 4. Template Rendering Issues

**Error:** `Template not found` or CSS not applied

**Solution:**
- Ensure you're using absolute paths for custom templates
- Check that `src/pdf/templates/` directory exists
- Verify template files are valid HTML/CSS

#### 5. Profile Picture Not Embedded

**Issue:** PDF generated without profile picture

**Possible Causes:**
- LinkedIn profile has no public photo
- Image download blocked by rate limiting
- Network connectivity issues

**Solution:** Tool will generate PDF without image and show warning

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
poetry run python -m src.cli --debug <profile-url>
```

### Getting Help

1. Check [Issues](https://github.com/alexcolls/linkedin-cv/issues) for similar problems
2. Enable debug mode and review logs
3. Open a new issue with:
   - Error message
   - Debug logs (remove sensitive info)
   - Your environment (OS, Python version, Poetry version)

## 🤝 Contributing

Contributions are welcome! This project follows standard open-source contribution practices.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests and quality checks:**
   ```bash
   poetry run pytest
   poetry run black src/ tests/
   poetry run flake8 src/ tests/
   poetry run mypy src/
   ```
5. **Commit your changes** (use emoji commits! 🎉)
   ```bash
   git commit -m "✨ Add amazing feature"
   ```
6. **Push to your fork** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Guidelines

- ✅ Write tests for new features
- ✅ Follow existing code style (Black formatting)
- ✅ Add type hints for all functions
- ✅ Update documentation for user-facing changes
- ✅ Keep commits atomic and well-described
- ✅ Use emoji in commit messages (see [gitmoji](https://gitmoji.dev/))

### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **isort** for import sorting

All enforced via pre-commit hooks.

### Testing Guidelines

- Write unit tests for business logic
- Use fixtures for test data
- Mock external dependencies (LinkedIn, network requests)
- Aim for >80% code coverage

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

✅ **You CAN:**
- Use commercially
- Modify the code
- Distribute
- Use privately

❌ **You CANNOT:**
- Hold the author liable
- Use the author's name for endorsement

📋 **You MUST:**
- Include the original license and copyright notice

## 👤 Author

**Alex Colls**

- GitHub: [@alexcolls](https://github.com/alexcolls)
- LinkedIn: [Alex Colls](https://www.linkedin.com/in/alexcolls/)

## 🙏 Acknowledgments

- **Playwright** - Excellent browser automation framework
- **WeasyPrint** - High-quality PDF generation from HTML/CSS
- **LinkedIn** - For providing the (imperfect) inspiration
- **Open Source Community** - For all the amazing tools and libraries

---

<p align="center">
  Made with ❤️ and Python
</p>

<p align="center">
  <a href="https://github.com/alexcolls/linkedin-cv">⭐ Star this repo if you find it useful!</a>
</p>

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/alexcolls/linkedin-cv?style=social)
![GitHub forks](https://img.shields.io/github/forks/alexcolls/linkedin-cv?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/alexcolls/linkedin-cv?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/alexcolls/linkedin-cv?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues/alexcolls/linkedin-cv?style=flat-square)
![GitHub pull requests](https://img.shields.io/github/issues-pr/alexcolls/linkedin-cv?style=flat-square)
