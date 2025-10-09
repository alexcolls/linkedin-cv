# LinkedIn Profile HTML Export Guide

This guide explains how to manually save your LinkedIn profile HTML to bypass authentication issues when generating your PDF CV.

## Why Export HTML Manually?

LinkedIn requires authentication to view full profile information. When using the scraper without being logged in, LinkedIn shows an authentication wall instead of your actual profile content. By manually saving the HTML while logged in, you can capture all your profile data for PDF generation.

## Step-by-Step Instructions

### Method 1: Using Browser Developer Tools (Recommended)

This method works in **Chrome, Firefox, Edge, and most modern browsers**.

#### 1. Open Your LinkedIn Profile

1. Log in to LinkedIn in your browser
2. Navigate to your profile page (click on "Me" → "View Profile")
3. Make sure you're viewing your **full profile** (the public view)
   - Your profile URL should look like: `https://www.linkedin.com/in/your-username/`

#### 2. Open Developer Tools

**Option A - Keyboard Shortcut:**
- **Windows/Linux**: Press `F12` or `Ctrl + Shift + I`
- **Mac**: Press `Cmd + Option + I`

**Option B - Menu:**
- **Chrome/Edge**: Click the three dots menu → More Tools → Developer Tools
- **Firefox**: Click the three lines menu → More Tools → Web Developer Tools

#### 3. Save the Complete HTML

**Method A - Save Outer HTML (Recommended):**

1. In the Developer Tools panel, click on the **"Elements"** tab (Chrome/Edge) or **"Inspector"** tab (Firefox)
2. In the HTML tree view, find the `<html>` tag at the very top
3. **Right-click** on the `<html>` tag
4. Select **"Edit as HTML"** (Chrome/Edge) or **"Edit as HTML"** (Firefox)
5. Press `Ctrl+A` (Windows/Linux) or `Cmd+A` (Mac) to select all the HTML
6. Press `Ctrl+C` (Windows/Linux) or `Cmd+C` (Mac) to copy
7. Open a text editor (Notepad, VS Code, etc.)
8. Paste the HTML and save it as `linkedin-profile.html`

**Method B - Copy Outer HTML:**

1. In the Developer Tools panel, click on the **"Elements"** tab
2. Right-click on the `<html>` tag at the top of the HTML tree
3. Select **"Copy"** → **"Copy outerHTML"**
4. Open a text editor and paste the content
5. Save the file as `linkedin-profile.html`

#### 4. Verify the HTML File

Open the saved HTML file in a text editor and verify:
- ✅ It contains your name
- ✅ It includes your work experience section
- ✅ It has your education details
- ✅ The file size is reasonable (typically 50KB - 500KB)

If the file is very small (<10KB), it might not have captured all the data. Try again or scroll through your profile first to load all sections.

### Method 2: Using "Save Page As" (Alternative)

This is a simpler but less reliable method.

1. Log in to LinkedIn and open your profile
2. Scroll through your entire profile to load all sections
3. Press `Ctrl+S` (Windows/Linux) or `Cmd+S` (Mac)
4. In the save dialog:
   - Choose **"Webpage, Complete"** or **"HTML Only"** (not "Single File")
   - Name the file `linkedin-profile.html`
   - Choose a location to save
5. Click **"Save"**

**Note:** This method may not capture dynamically loaded content as reliably as Method 1.

### Method 3: Using Browser Console (Advanced)

For advanced users who want a quick copy-paste solution:

1. Open your LinkedIn profile while logged in
2. Open Developer Tools (`F12`)
3. Go to the **"Console"** tab
4. Paste and run this command:

```javascript
copy(document.documentElement.outerHTML);
```

5. The complete HTML is now in your clipboard
6. Paste it into a text editor and save as `linkedin-profile.html`

## Tips for Better Results

### Before Saving HTML:

1. **Scroll Through Your Profile**: Scroll down to the bottom of your profile page to ensure all lazy-loaded sections are loaded
2. **Expand Sections**: Click "Show more" on truncated sections (About, Experience descriptions, etc.)
3. **Wait for Images**: Let all profile pictures and images load completely
4. **Use Your Public Profile**: Make sure you're viewing the public version of your profile, not the edit mode

### File Location:

Save the HTML file in a convenient location, such as:
- `~/Downloads/linkedin-profile.html`
- Your project directory: `/home/quantium/labs/linkedin-cv/linkedin-profile.html`

## Using the HTML File with LinkedIn CV Generator

Once you have your HTML file, generate your PDF CV with:

```bash
# Using absolute path
poetry run python -m src.cli --html-file /path/to/linkedin-profile.html

# Or with a specific output directory
poetry run python -m src.cli --html-file linkedin-profile.html -o ./output

# With a custom template
poetry run python -m src.cli --html-file linkedin-profile.html -t custom_template.html
```

## Troubleshooting

### Problem: PDF is empty or missing sections

**Solutions:**
- Make sure you scrolled through your entire profile before saving
- Try Method 1 (Developer Tools) instead of "Save Page As"
- Verify the HTML file contains your data (open it in a text editor)
- Check that file size is reasonable (should be > 50KB for a typical profile)

### Problem: "Authentication Wall" content in PDF

**Solutions:**
- You saved the HTML while **not logged in** - log in to LinkedIn first
- You might have saved the wrong page - make sure URL is `linkedin.com/in/your-username/`

### Problem: Images missing in PDF

**Solutions:**
- Wait for all images to load before saving HTML
- Images might be blocked by your privacy settings - try using your public profile
- The image processor will handle most external images, but some may require authentication

### Problem: "Recent Activity" or dynamic content missing

**Solutions:**
- This is expected - we focus on static profile sections (Experience, Education, Skills)
- Scroll through your profile before saving to trigger loading of lazy content

## Privacy Note

⚠️ **Important**: The HTML file will contain your complete profile data. Store it securely and don't share it publicly if it contains sensitive information.

## Alternative: JSON Input (Coming Soon)

We're working on a feature to manually input profile data via JSON/YAML files for complete control over the CV content. Stay tuned!

## Need Help?

If you encounter issues:
1. Check that your HTML file is valid (open it in a browser - should show your profile)
2. Enable debug mode: `--debug` flag
3. File an issue on GitHub with:
   - Browser type and version
   - File size of the HTML
   - Any error messages

---

**Happy CV generating!** 📄✨
