# New Workflow: Complete LinkedIn Data Extraction

## Overview

The LinkedIn CV Generator now uses a **3-step workflow** that ensures complete data extraction by scraping dedicated detail pages instead of relying on the truncated main profile page.

## Why This Approach?

LinkedIn's main profile page often truncates content:
- Experience entries may be collapsed
- Skills list shows only top items
- Education details are abbreviated
- Certifications, projects, and other sections may be incomplete

The detail pages (`/details/experience/`, `/details/skills/`, etc.) contain the **complete, untruncated data**.

## Workflow Steps

### 1. 🌐 Extract HTML from LinkedIn Profile

**Menu Option 1** | **CLI**: `--extract-html`

This step scrapes all LinkedIn profile sections and saves raw HTML files:

```bash
./run.sh  # Select option 1
# or
poetry run python -m src.cli "profile-url" --extract-html
```

**What it does:**
- Scrapes the main profile page
- Scrapes all detail pages:
  - `/details/experience/` - Complete experience list
  - `/details/education/` - Full education details
  - `/details/skills/` - All skills with endorsements
  - `/details/certifications/` - Certifications
  - `/details/projects/` - Projects
  - `/details/languages/` - Languages
  - `/details/volunteering/` - Volunteer work
  - `/details/honors/` - Honors and awards
  - `/details/publications/` - Publications

**Output:**
```
output/
└── <username>/
    └── html/
        ├── profile.html
        ├── experience.html
        ├── education.html
        ├── skills.html
        ├── certifications.html
        ├── projects.html
        ├── languages.html
        ├── volunteer.html
        ├── honors.html
        ├── publications.html
        └── metadata.json
```

Also saves debug copies in project root: `last_scraped_<section>.html`

---

### 2. 📊 Extract JSON Data from HTML

**Menu Option 2** | **CLI**: `--parse-html <username>`

This step parses the saved HTML files and extracts structured JSON data:

```bash
./run.sh  # Select option 2
# or
poetry run python -m src.cli --parse-html "username"
```

**What it does:**
- Reads all HTML files from `output/<username>/html/`
- Parses each section using specialized parsers:
  - `parse_experience_detail()` - Extracts complete experience entries
  - `parse_education_detail()` - Extracts full education details
  - `parse_skills_detail()` - Extracts all skills with endorsement counts
  - Standard parsers for other sections
- Merges all data into a single JSON file

**Output:**
```
output/
└── <username>/
    ├── html/
    │   └── ... (HTML files from step 1)
    └── profile_data.json  ← Complete structured data
```

**JSON Structure:**
```json
{
  "name": "John Doe",
  "headline": "Software Engineer at Company",
  "location": "San Francisco, CA",
  "about": "Full bio text...",
  "experience": [
    {
      "title": "Senior Software Engineer",
      "company": "Company Name",
      "location": "San Francisco, CA",
      "duration": "Jan 2020 - Present · 4 yrs",
      "description": "Complete job description..."
    }
  ],
  "education": [...],
  "skills": [
    {
      "name": "Python",
      "endorsements": 99
    }
  ],
  "_metadata": {
    "extracted_at": "2024-01-15T10:30:00",
    "parsed_at": "2024-01-15T10:35:00",
    "profile_url": "https://www.linkedin.com/in/username/",
    "username": "username"
  }
}
```

---

### 3. 📄 Generate CV PDF from JSON

**Menu Option 3** | **CLI**: `--generate-pdf <username>`

This step generates a professional PDF CV from the JSON data:

```bash
./run.sh  # Select option 3
# or
poetry run python -m src.cli --generate-pdf "username"
```

**What it does:**
- Reads `output/<username>/profile_data.json`
- Downloads and processes profile picture (if available)
- Generates professional PDF using template
- Saves with timestamped filename

**Output:**
```
output/
└── <username>/
    ├── html/
    │   └── ... (HTML files)
    ├── profile_data.json
    └── cv_20240115_103500.pdf  ← Final PDF CV
```

---

## Benefits of This Approach

### ✅ Complete Data Extraction
- All experience entries (not just recent ones)
- Full skill list with endorsements
- Complete education details
- All certifications, projects, etc.

### ✅ Better Debugging
- Raw HTML saved for each section
- Can re-parse without re-scraping
- Easy to diagnose parsing issues

### ✅ Flexible Pipeline
- Extract once, generate multiple times
- Test different PDF templates without re-scraping
- Modify parsing logic and re-run step 2 only

### ✅ Reduced Rate Limiting Risk
- Scraping happens once (step 1)
- No need to repeatedly access LinkedIn
- Can work offline after step 1

---

## Authentication

Before running step 1, make sure you're authenticated:

**Option A: Login via browser (recommended)**
```bash
./run.sh  # Select option 4 - Login to LinkedIn
```

**Option B: Extract cookies from Chrome**
```bash
./run.sh  # Select option 5 - Extract cookies from Chrome
```

See [AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md) for details.

---

## Troubleshooting

### Empty or Incomplete Data After Step 1
- **Cause**: Not authenticated to LinkedIn
- **Solution**: Run option 4 (Login) before extracting HTML
- Check `last_scraped_profile.html` - if you see masked content (*****), authentication failed

### "HTML directory not found" Error in Step 2
- **Cause**: Step 1 wasn't completed successfully
- **Solution**: Run step 1 first to extract HTML files

### "JSON file not found" Error in Step 3
- **Cause**: Step 2 wasn't completed successfully
- **Solution**: Run step 2 first to generate JSON data

### Parsing Issues
- Check the HTML files in `output/<username>/html/`
- Look at `last_scraped_<section>.html` files for debugging
- Enable debug mode: `--debug` flag or set in menu

---

## Comparison: Old vs New Workflow

### Old Workflow (Single Step)
```
LinkedIn → Scrape Profile → Parse → Generate PDF
                ↓
    May have incomplete/truncated data
```

### New Workflow (Three Steps)
```
Step 1: LinkedIn → Scrape All Detail Pages → Save HTML
Step 2: HTML Files → Parse All Sections → Save JSON
Step 3: JSON Data → Generate PDF → Professional CV
              ↓
    Complete, untruncated data from detail pages
```

---

## Advanced Usage

### Re-parse Without Re-scraping
If you want to improve parsing logic or fix a bug:
```bash
# No need to re-run step 1!
poetry run python -m src.cli --parse-html "username" --debug
```

### Generate Multiple PDF Versions
Try different templates or formats:
```bash
poetry run python -m src.cli --generate-pdf "username"
# Modify template or JSON
poetry run python -m src.cli --generate-pdf "username" --template custom.html
```

### Batch Processing
Extract data for multiple profiles:
```bash
for profile in user1 user2 user3; do
  poetry run python -m src.cli "https://linkedin.com/in/$profile" --extract-html
done
```

---

## Next Steps

After completing the workflow, you'll have:
- ✅ Complete HTML data saved locally
- ✅ Structured JSON data
- ✅ Professional PDF CV ready to send

You can regenerate the PDF anytime by running step 3 again!
