# HTML Export Guide

## Overview

This guide explains how to manually export your LinkedIn profile as HTML and use it with the LinkedIn CV Generator. This workflow is useful when:

- You encounter authentication issues
- LinkedIn blocks automated scraping
- You want to work with a saved snapshot of your profile
- You need to troubleshoot data extraction

---

## Why Manual HTML Export?

### Advantages
✅ **No Authentication Required** - Export once, use multiple times  
✅ **Reliable** - Always have your profile data available  
✅ **Fast** - No browser automation needed  
✅ **Debugging** - Inspect HTML directly before PDF generation  
✅ **Offline** - Process HTML files without internet connection  

### When to Use

| Situation | Recommendation |
|-----------|-----------------|
| First time using tool | ✅ Use auto-scraping |
| LinkedIn authentication working | ✅ Use auto-scraping |
| Frequent PDF generation | ✅ Export HTML once, reuse |
| Authentication issues | ✅ Use HTML export workflow |
| Troubleshooting data extraction | ✅ Use HTML export workflow |
| Batch processing profiles | ✅ Export HTML first |

---

## Step 1: Export Profile HTML (Chrome)

### Instructions

1. **Open LinkedIn Profile**
   - Go to your LinkedIn profile: https://www.linkedin.com/in/yourprofile/
   - Make sure you're logged in
   - Wait for all content to load

2. **Open Developer Tools**
   - Press `F12` on your keyboard
   - Or: Right-click → Inspect
   - Or: `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac)

3. **Copy Full HTML**
   - Click on the "Elements" or "Inspector" tab
   - Right-click on the `<html>` tag (top level)
   - Select "Copy" → "Copy entire element"
   - Or: Press `Ctrl+A` to select all, then `Ctrl+C` to copy

4. **Save to File**
   - Open a text editor (VS Code, Notepad++, Sublime, etc.)
   - Paste the HTML content
   - Save as: `linkedin_profile.html`
   - Choose location: Any folder you prefer

### Chrome Screenshot Guide

```
1. Right-click anywhere on page → Inspect (or Press F12)
2. In DevTools, find the <html> tag
3. Right-click it → Copy → Copy entire element
4. Paste in text editor → Save as .html file
```

---

## Step 2: Export Profile HTML (Firefox)

### Instructions

1. **Open LinkedIn Profile**
   - Navigate to your profile
   - Ensure you're logged in

2. **Open Developer Tools**
   - Press `F12` on your keyboard
   - Or: Right-click → Inspect Element
   - Or: `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac)

3. **Select HTML**
   - Click "Inspector" tab
   - Click the element selector icon (top-left)
   - Click on the page content
   - Right-click the `<html>` tag
   - Select "Copy" → "Copy outer HTML"

4. **Save to File**
   - Paste into text editor
   - Save as: `linkedin_profile.html`

### Firefox Tips

- Use "Copy outer HTML" to get the complete `<html>` element
- Make sure the full page has loaded before exporting
- JavaScript may still be running; disable it if needed

---

## Step 3: Export Additional Sections (Optional)

For complete data extraction, export these pages separately:

### LinkedIn Detail Pages to Export

```
Experience:     /in/username/details/experience/
Education:      /in/username/details/education/
Skills:         /in/username/details/skills/
Certifications: /in/username/details/certifications/
Languages:      /in/username/details/languages/
Projects:       /in/username/details/projects/
Volunteer:      /in/username/details/volunteering/
Honors:         /in/username/details/honors/
Publications:   /in/username/details/publications/
```

### Export Each Section

1. Navigate to detail page URL
2. Wait for content to load
3. Follow Step 1-4 above
4. Save as: `section_name.html` (e.g., `experience.html`)

---

## Step 4: Using HTML Files with LinkedIn CV Generator

### Option A: Generate PDF from HTML File

```bash
# Using the tool directly
linkedin-cv --html-file /path/to/linkedin_profile.html

# Or via the interactive menu
./run.sh
# Select: 3) Extract HTML from profile
# (It will ask for HTML file location)
```

### Option B: Using Full Workflow

```bash
# 1. Extract JSON from saved HTML files
./run.sh
# Select: 2) Extract JSON data
# Paste your HTML file path when prompted

# 2. Verify output
ls output/
# Check profile_data.json

# 3. Generate PDF from JSON
./run.sh
# Select: option to generate PDF from JSON
```

### Option C: Command Line

```bash
# Single command
linkedin-cv --html-file ~/Downloads/linkedin_profile.html

# With custom output
linkedin-cv --html-file ~/Downloads/linkedin_profile.html \
    --output-dir ~/my_cvs \
    --template custom_template.html
```

---

## Troubleshooting

### HTML File is Too Large

**Problem**: File is 5MB+, won't open properly

**Solution**:
- Remove unnecessary scripts: Search for `<script>` tags and delete them
- LinkedIn embeds many tracking scripts that aren't needed
- Keep the main `<main>` element and content divs

**Manual Cleanup**:
```bash
# Extract just the main content
# Use a tool like https://www.html-cleaner.com/
# Or manually delete <script> tags
```

### "Content is masked with asterisks"

**Problem**: Profile data shows `*****` instead of actual content

**Causes**:
1. Not logged in when exporting HTML
2. HTML is cached/outdated
3. Exported unauthenticated version

**Solution**:
- Make sure you're logged in to LinkedIn before exporting
- Export a fresh copy (not an old file)
- Check browser's privacy mode isn't interfering

### HTML File Missing Sections

**Problem**: Some profile sections are missing from exported HTML

**Reasons**:
1. Section wasn't visible on the profile
2. Page didn't load completely
3. Lazy-loaded content not triggered

**Solution**:
- Scroll through entire profile before exporting
- Wait 3-5 seconds for all content to load
- Export again if needed

### "File not found" Error

**Problem**: Tool can't find the HTML file

**Solution**:
- Use absolute paths: `/home/user/Downloads/file.html` (not `~/Downloads/file.html`)
- Or: Use the tool's file picker dialog
- Check file actually exists: `ls -la /path/to/file.html`

---

## File Organization

### Recommended Directory Structure

```
my_linkedin_exports/
├── alex-colls/
│   ├── linkedin_profile.html
│   ├── experience.html
│   ├── education.html
│   ├── skills.html
│   └── certifications.html
├── jane-doe/
│   ├── linkedin_profile.html
│   └── experience.html
└── .env
```

### Using with Tool

```bash
# Method 1: Point to individual files
linkedin-cv --html-file ~/my_linkedin_exports/alex-colls/linkedin_profile.html

# Method 2: Let tool discover files
./run.sh
# Enter path when prompted
# Tool will look for HTML files in that directory
```

---

## Advanced: Programmatic HTML Export

### Using Browser Console

You can export HTML directly from browser console:

```javascript
// Copy all HTML
copy(document.documentElement.outerHTML);

// Or save to file (requires DevTools)
// 1. Right-click in console
// 2. Select "Save as..."
// 3. Save with .html extension
```

### Using Playwright (Like LinkedIn CV Generator)

```bash
# If you want to script HTML exports
./run.sh
# Select: 3) Extract HTML from profile
# Tool handles everything automatically
```

---

## Comparing Workflows

### Workflow 1: Direct Scraping (Recommended)
```
✅ Pros:  Always up-to-date, automatic, no manual steps
❌ Cons: Requires authentication, LinkedIn may block
```

**Use when**: Authentication works, you want current data

### Workflow 2: HTML Export (Reliable)
```
✅ Pros:  Offline, fast, no automation needed
❌ Cons: Manual export, needs updating, must be authenticated once
```

**Use when**: Need reliable workflow, updating profile occasionally

### Workflow 3: Hybrid (Best of Both)
```
✅ Pros:  Use auto-scraping normally, fall back to HTML if needed
❌ Cons: Need to maintain both methods
```

**Use when**: Want flexibility for different situations

---

## Batch Processing Multiple Profiles

### Setup

1. **Create folder structure**:
```bash
mkdir batch_exports
cd batch_exports

# Create subfolders for each person
mkdir alice
mkdir bob
mkdir charlie
```

2. **Export HTML for each profile**:
- Login to each LinkedIn profile
- Follow steps above
- Save in corresponding folder:
  - `batch_exports/alice/profile.html`
  - `batch_exports/bob/profile.html`
  - `batch_exports/charlie/profile.html`

3. **Generate CVs**:
```bash
# For each profile
for dir in batch_exports/*/; do
    linkedin-cv --html-file "$dir/profile.html"
done

# Check outputs
ls output/
```

---

## Performance Tips

### Export Speed

- **Faster**: Direct scraping with auto-login (usually 30-60 seconds)
- **Slower**: Manual HTML export (5 minutes including setup)
- **Fastest**: Reusing exported HTML (5-10 seconds per PDF)

### File Size Optimization

- Original export: 2-5MB
- After removing scripts: 500KB-1MB
- Recommended: Keep original, tool handles cleanup

### Caching Strategy

```bash
# Export once (5 min)
linkedin-cv --html-file ~/profile_export.html -o ~/output1

# Reuse same file (5 sec each)
linkedin-cv --html-file ~/profile_export.html -o ~/output2
linkedin-cv --html-file ~/profile_export.html -o ~/output3
```

---

## Security Considerations

### Protecting Your HTML Files

⚠️ **Warning**: HTML files contain personal information:
- Your name, location, contact info
- Job history and current employer
- Education and skills
- Connections (if visible)

### Best Practices

✅ **Do:**
- Store in private folder with restricted permissions
- Use `.gitignore` to prevent accidental commits
- Delete old exports when no longer needed
- Encrypt sensitive exports

❌ **Don't:**
- Upload to public repositories
- Share via unsecured channels
- Store in cloud without encryption
- Leave on public shared computers

### Permission Management

```bash
# Restrict file access (owner only)
chmod 600 ~/linkedin_profile.html

# Remove file securely
shred -u ~/linkedin_profile.html  # Linux
rm -P ~/linkedin_profile.html     # macOS
```

---

## FAQ

### Q: How often should I export new HTML?

**A:** Export when your profile changes significantly:
- Job changes
- New certifications
- Updated skills
- Major resume updates

For monthly CV updates, re-export every 2-4 weeks.

### Q: Can I use HTML from other LinkedIn profiles?

**A:** Yes, if you have access (e.g., a recruiter exporting candidate profiles). Follow the same process.

### Q: Does HTML export work offline?

**A:** Yes! Once exported, you can process HTML files without internet:
```bash
linkedin-cv --html-file /offline/profile.html
```

### Q: Why is my exported HTML so large?

**A:** LinkedIn includes:
- Embedded tracking scripts (Google Analytics, etc.)
- Styling and assets
- Lazy-loaded content
- Duplicate content for responsive design

It's normal for files to be 2-5MB.

### Q: Can I edit the HTML before processing?

**A:** Yes, but carefully:
- Tool expects standard LinkedIn HTML structure
- Removing `<main>` or section divs breaks extraction
- Safe to remove: `<script>`, unused CSS, comments

### Q: How do I know which HTML sections are needed?

**A:** All are useful:
- **Main profile** - Header, about, stats
- **Experience** - Detailed job descriptions
- **Education** - Degree details
- **Skills** - Full skill list
- **Other sections** - Certifications, languages, etc.

Export all if you want complete data.

---

## Next Steps

### After HTML Export

1. ✅ Verify file exists and has content
2. ✅ Generate initial CV to test
3. ✅ Check output for missing data
4. ✅ Troubleshoot any issues using guide above
5. ✅ Store file safely for future use

### Updating Your CV

```bash
# When profile updates:
# 1. Export fresh HTML
linkedin-cv --html-file ~/new_profile.html -o ~/output_v2

# 2. Compare with previous
diff ~/output/cv.pdf ~/output_v2/cv.pdf

# 3. Use updated version
cp ~/output_v2/* ~/final_cvs/
```

---

## Additional Resources

- **LinkedIn Help**: https://www.linkedin.com/help
- **Browser DevTools Docs**:
  - Chrome: https://developer.chrome.com/docs/devtools/
  - Firefox: https://developer.mozilla.org/en-US/docs/Tools
- **HTML Cleaning Tools**: https://www.html-cleaner.com/
- **LinkedIn CV Generator Docs**: See README.md

---

## Support

If you encounter issues:

1. Check troubleshooting section above
2. Review `/home/quantium/labs/linkedin-cv/docs/TROUBLESHOOTING_EMPTY_DATA.md`
3. Check file permissions and paths (use absolute paths)
4. Try re-exporting HTML fresh
5. Check that you were logged in when exporting

---

*Last Updated: 2025-10-20*  
*Version: 0.5.2*  
*Compatible with: Chrome, Firefox, Safari*
