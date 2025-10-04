# Usage Guide

This guide provides step-by-step instructions for using LinkedIn CV Generator.

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/alexcolls/linkedin-cv.git
cd linkedin-cv

# Install dependencies
poetry install

# Install Playwright browsers
poetry run playwright install chromium
```

### 2. Generate Your First CV

```bash
# Basic usage - generates PDF in ./output/
poetry run python -m src.cli https://www.linkedin.com/in/your-username/
```

That's it! Your professional PDF CV will be generated in the `output/` directory.

## Detailed Usage

### Command-Line Options

```bash
poetry run python -m src.cli [OPTIONS] <linkedin-profile-url>
```

**Required:**
- `<linkedin-profile-url>`: Your LinkedIn profile URL (e.g., `https://www.linkedin.com/in/johndoe/`)

**Options:**
- `-o, --output-dir PATH`: Output directory for PDFs (default: `./output`)
- `-t, --template PATH`: Custom HTML template path (optional)
- `--headless / --no-headless`: Run browser in headless mode (default: headless)
- `--debug`: Enable debug logging
- `--help`: Show help message

### Examples

#### Basic Usage

Generate a CV from your LinkedIn profile:

```bash
poetry run python -m src.cli https://www.linkedin.com/in/johndoe/
```

**Output:**
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
   ✓ Profile scraped successfully!

📋 Parsing profile data...
   ✓ Parsed 8 sections!

📸 Processing profile picture...
   ✓ Profile picture ready!

📄 Generating PDF...
   ✓ PDF generated successfully!

✅ Done! Your CV is ready at:
   output/john-doe_2025-10-04-032234.pdf
```

#### Custom Output Directory

Save the PDF to a specific directory:

```bash
poetry run python -m src.cli -o ~/Documents/CVs https://www.linkedin.com/in/johndoe/
```

#### Debug Mode

Enable debug logging and see the browser in action:

```bash
poetry run python -m src.cli --no-headless --debug https://www.linkedin.com/in/johndoe/
```

This is useful for:
- Troubleshooting scraping issues
- Verifying what data is being extracted
- Handling authentication prompts

#### Custom Template

Use your own HTML template:

```bash
poetry run python -m src.cli -t /absolute/path/to/my_template.html https://www.linkedin.com/in/johndoe/
```

## Common Workflows

### 1. Job Application

Generate a fresh CV before applying:

```bash
poetry run python -m src.cli -o ~/Applications/CompanyName https://www.linkedin.com/in/your-username/
```

### 2. Portfolio Update

Keep multiple dated versions:

```bash
# PDFs are automatically timestamped
poetry run python -m src.cli https://www.linkedin.com/in/your-username/

# Result: your-username_2025-10-04-032234.pdf
```

### 3. Testing Custom Design

Test your custom template:

```bash
poetry run python -m src.cli -t custom_template.html --debug https://www.linkedin.com/in/your-username/
```

## Tips & Best Practices

### 1. Keep Your LinkedIn Updated

The tool scrapes whatever is on your LinkedIn profile. Make sure your profile is complete and up-to-date before generating the CV.

**Key sections to update:**
- ✅ Profile picture (high quality, professional)
- ✅ Headline (clear and descriptive)
- ✅ About/Summary (compelling overview)
- ✅ Experience (detailed descriptions)
- ✅ Education (complete information)
- ✅ Skills (relevant to your field)
- ✅ Certifications (with dates)

### 2. Public Profile

Ensure your LinkedIn profile is set to public or accessible without login. If the tool encounters a login wall:

```bash
# Use non-headless mode to manually log in
poetry run python -m src.cli --no-headless https://www.linkedin.com/in/your-username/
```

### 3. Regenerate Regularly

Update your CV whenever you make changes to LinkedIn:

```bash
# Quick regeneration
poetry run python -m src.cli https://www.linkedin.com/in/your-username/
```

The timestamp in the filename helps track versions.

### 4. Customize the Template

The default template is beautiful, but you can customize it:

1. Copy the default template:
   ```bash
   cp src/pdf/templates/cv_template.html my_custom_template.html
   ```

2. Modify HTML structure or styling

3. Use it:
   ```bash
   poetry run python -m src.cli -t /absolute/path/to/my_custom_template.html https://www.linkedin.com/in/your-username/
   ```

### 5. Batch Processing

Generate CVs for multiple profiles (if you have permission):

```bash
#!/bin/bash
profiles=(
    "https://www.linkedin.com/in/profile1/"
    "https://www.linkedin.com/in/profile2/"
)

for profile in "${profiles[@]}"; do
    poetry run python -m src.cli "$profile"
done
```

## Template Customization

### Available Variables

Your template has access to all profile data:

```jinja2
{{ name }}                    # Full name
{{ headline }}                # Professional headline
{{ location }}                # Location
{{ profile_image_data }}      # Base64 image data URI
{{ about }}                   # About/Summary text

{{ experience }}              # List of experience items
{{ education }}               # List of education items
{{ skills }}                  # List of skills
{{ certifications }}          # List of certifications
{{ languages }}               # List of languages
{{ volunteer }}               # List of volunteer work
{{ projects }}                # List of projects
{{ publications }}            # List of publications
{{ honors }}                  # List of honors & awards
{{ courses }}                 # List of courses
```

### Experience Item Structure

```python
{
    "title": "Software Engineer",
    "company": "Tech Corp",
    "duration": "2020 - Present",
    "location": "San Francisco, CA",
    "description": "Full description..."
}
```

### Education Item Structure

```python
{
    "institution": "University Name",
    "degree": "Bachelor of Science",
    "field": "Computer Science",
    "duration": "2016 - 2020"
}
```

## Troubleshooting

### Issue: "Browser executable not found"

**Solution:**
```bash
poetry run playwright install chromium
```

### Issue: "Cannot access profile (login required)"

**Solution:**
Use non-headless mode and manually log in:
```bash
poetry run python -m src.cli --no-headless https://www.linkedin.com/in/your-username/
```

### Issue: "Profile picture not embedded"

**Possible causes:**
- No public profile picture
- Network issues
- Rate limiting

**Solution:**
- Check if your LinkedIn photo is public
- Try again later
- The CV will still generate without the photo

### Issue: "WeasyPrint errors"

**Ubuntu/Debian:**
```bash
sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**macOS:**
```bash
brew install cairo pango gdk-pixbuf libffi
```

## Advanced Usage

### Using as a Python Module

```python
import asyncio
from pathlib import Path
from src.scraper.linkedin_scraper import LinkedInScraper
from src.scraper.parser import ProfileParser
from src.pdf.generator import PDFGenerator
from src.utils.image_processor import ImageProcessor

async def generate_cv(profile_url: str):
    # Scrape profile
    scraper = LinkedInScraper(headless=True)
    html_content = await scraper.scrape_profile(profile_url)

    # Parse data
    parser = ProfileParser()
    profile_data = parser.parse(html_content)

    # Process image
    if profile_data.get("profile_picture_url"):
        processor = ImageProcessor()
        profile_data["profile_image_data"] = processor.process(
            profile_data["profile_picture_url"]
        )

    # Generate PDF
    generator = PDFGenerator()
    output_path = Path("output") / f"{profile_data['username']}.pdf"
    generator.generate(profile_data, str(output_path))

    return output_path

# Run
asyncio.run(generate_cv("https://www.linkedin.com/in/your-username/"))
```

### Scheduled CV Updates

Set up a cron job to regenerate your CV weekly:

```bash
# Edit crontab
crontab -e

# Add this line (runs every Monday at 9 AM)
0 9 * * 1 cd /home/quantium/labs/linkedin-cv && /home/quantium/.local/bin/poetry run python -m src.cli https://www.linkedin.com/in/your-username/
```

## Getting Help

If you encounter issues:

1. **Enable debug mode:**
   ```bash
   poetry run python -m src.cli --debug https://www.linkedin.com/in/your-username/
   ```

2. **Check the logs** in your terminal output

3. **Open an issue** on GitHub with:
   - Error message
   - Debug output (remove sensitive info)
   - Your environment (OS, Python version)

4. **Review README.md** for additional troubleshooting

## Next Steps

- ⭐ Star the repository if you find it useful
- 🐛 Report bugs or request features via GitHub Issues
- 🤝 Contribute improvements via Pull Requests
- 📢 Share with colleagues who need better CVs

---

**Happy CV generation!** 🎉
