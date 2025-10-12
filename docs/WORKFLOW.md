# Workflow: LinkedIn Profile Extraction Options

## Overview

The LinkedIn CV Generator provides **three workflow options** for different use cases:

1. **Generate CV PDF** - All-in-one solution (recommended for most users)
2. **Extract JSON data** - For data analysis or custom processing
3. **Extract HTML** - For debugging or advanced parsing

## Quick Comparison

| Option | What It Does | Output | Intermediate Files |
|--------|-------------|--------|-------------------|
| **1. Generate PDF** | Scrape → Parse → PDF | `username_timestamp.pdf` | Currently keeps files |
| **2. Extract JSON** | Scrape → Parse → JSON | `profile_data.json` | Removes HTML |
| **3. Extract HTML** | Scrape only | HTML files | Keeps all HTML |

---

## Workflow Options

### 1. 📄 Generate CV PDF (Recommended)

**Menu Option 1** | **Default workflow**

The simplest workflow - generates a professional PDF CV directly from your LinkedIn profile.

```bash
./run.sh  # Select option 1
# or
./run.sh username
poetry run python -m src.cli "profile-url"
```

**What it does:**

1. Scrapes your LinkedIn profile
2. Parses all sections (experience, education, skills, etc.)
3. Generates a professional PDF CV

**Output:**

```
output/
└── <username>/
    └── username_20250112_143000.pdf
```

**Best for:**
- First-time users
- Quick CV generation
- Standard use cases

---

### 2. 📊 Extract JSON Data

**Menu Option 2** | **CLI**: `--json`

Exports structured JSON data for analysis, integration, or custom processing.

```bash
./run.sh  # Select option 2
# or
poetry run python -m src.cli "profile-url" --json
```

**What it does:**

1. Scrapes your LinkedIn profile (all sections)
2. Parses and extracts structured data
3. Saves to JSON file
4. 🧹 Cleans up HTML files (removed after parsing)

**Output:**

```
output/
└── <username>/
    └── profile_data.json
```

**Best for:**
- Data analysis
- Custom integrations
- Backup of profile data
- Multiple export formats

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

### 3. 🌐 Extract HTML from Profile (Advanced)

**Menu Option 3** | **CLI**: `--extract-html`

Scrapes all LinkedIn profile sections and saves raw HTML for debugging or advanced parsing.

```bash
./run.sh  # Select option 3
# or
poetry run python -m src.cli "profile-url" --extract-html
```

**What it does:**

1. Scrapes the main profile page
2. Scrapes **all detail pages** (for complete data):
   - `/details/experience/` - Full experience list
   - `/details/education/` - Complete education
   - `/details/skills/` - All skills with endorsements
   - `/details/certifications/` - Certifications
   - `/details/projects/` - Projects  
   - `/details/languages/` - Languages
   - `/details/volunteering/` - Volunteer work
   - `/details/honors/` - Honors and awards
   - `/details/publications/` - Publications
3. Saves all raw HTML files

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

**Best for:**
- Debugging parsing issues
- Inspecting raw LinkedIn HTML
- Developing custom parsers
- Re-parsing without re-scraping

---

## Why Multiple Options?

### 📄 Option 1: For Most Users
- **Simple**: One command, one PDF
- **Fast**: No intermediate steps
- **Complete**: Gets all your data

### 📊 Option 2: For Data Users
- **Structured**: Clean JSON format
- **Portable**: Use data anywhere
- **No HTML clutter**: Automatic cleanup

### 🌐 Option 3: For Developers
- **Complete**: All detail pages scraped
- **Debuggable**: Inspect raw HTML
- **Flexible**: Parse multiple times
- **Offline**: Work without re-scraping

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

### Empty or Incomplete Data

- **Cause**: Not authenticated to LinkedIn
- **Solution**: Run option 4 (Login to LinkedIn) first
- Check the HTML files in output directory - if you see masked content (**\***), authentication failed

### Parsing Issues

- Check the HTML files in `output/<username>/html/`
- Enable debug mode: `--debug` flag for detailed logging
- Verify authentication by checking if HTML contains asterisks (*****)

---

## File Cleanup

### Option 1 (Generate PDF)
- Currently: Keeps all intermediate files
- Future: Will clean up HTML/JSON after PDF generation

### Option 2 (Extract JSON)  
- ✅ Removes HTML files after parsing
- 💾 Keeps only JSON file

### Option 3 (Extract HTML)
- 💾 Keeps all HTML files
- For debugging and inspection

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
