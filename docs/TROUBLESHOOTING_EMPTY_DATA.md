# Troubleshooting: Empty or Minimal Profile Data

## Problem

When exporting LinkedIn profile data to JSON, you get minimal information:

```json
{
  "username": "linkedin-profile",
  "name": "John Doe",
  "headline": "Software Engineer",
  "location": "San Francisco, CA",
  "experience": [],  ← EMPTY
  "education": [],   ← EMPTY
  "skills": [],      ← EMPTY
  "about": null,     ← EMPTY
  ...
}
```

## Root Cause

**You are not authenticated with LinkedIn.** 

LinkedIn restricts profile data for non-authenticated users. When you're not logged in, LinkedIn only shows:
- Name
- Headline
- Location  
- Profile picture

All other data (experience, education, skills, etc.) is hidden behind authentication.

## Solution

You need to authenticate with LinkedIn before scraping. There are **two methods**:

### Method 1: Interactive Login (Recommended)

1. Run the menu: `./run.sh`
2. Select option **3** - "🔐 Login to LinkedIn"
3. A browser will open - log in with your LinkedIn credentials
4. Your session will be saved for ~30 days
5. Try exporting/generating again (option 1 or 2)

```bash
./run.sh
# Select: 3
# Follow browser prompts to log in
# Then try again with option 1 or 2
```

### Method 2: Extract Cookies from Chrome

If you're already logged into LinkedIn in Chrome:

1. Make sure Chrome is **closed** (or it may be locked)
2. Run the menu: `./run.sh`
3. Select option **4** - "🍪 Extract cookies from Chrome"
4. Try exporting/generating again (option 1 or 2)

```bash
./run.sh
# Select: 4
# Then try again with option 1 or 2
```

## How to Verify Authentication

After logging in, the tool will now show a warning when minimal data is extracted:

```
⚠️  WARNING: Only basic profile data was extracted!
   This usually means you're not logged in to LinkedIn.

To fix this:
  1. Run the login command: ./run.sh → option 3
  2. Or extract cookies: ./run.sh → option 4
  3. Then try exporting again
```

When authentication is working correctly, you'll see:
```
✓ Parsed 15+ sections!  (instead of just 4)
```

## Debugging

### Check Saved HTML

The scraper now automatically saves the HTML it retrieves to `last_scraped.html`. 

Check this file to see what LinkedIn is actually returning:

```bash
# View the saved HTML
less last_scraped.html

# Search for content indicators
grep -i "experience" last_scraped.html
grep -i "education" last_scraped.html
```

If the HTML contains minimal content, authentication failed.

### Check Session File

Your LinkedIn session is stored in:
```
~/.linkedin_session.json
```

If this file is old (>30 days) or corrupted, delete it and re-authenticate:

```bash
# Remove old session
rm ~/.linkedin_session.json

# Re-authenticate
./run.sh  # Option 3
```

### Run with Debug Mode

For detailed logging:

```bash
poetry run python -m src.cli --debug --json "username"
```

This will show:
- Browser launch details
- Authentication status
- HTML content size
- Parser results

## Technical Details

### What Gets Saved

- **Session cookies**: `~/.linkedin_session.json`
- **Debug HTML**: `last_scraped.html` (in project root)
- **Output data**: `output/<username>/profile_data.json`

### Authentication Methods Used

1. **Chrome persistent context**: Uses your logged-in Chrome profile
2. **Session file**: Uses saved cookies from previous login
3. **Cookie extraction**: Extracts cookies from Chrome's cookie database

### Data Detection

The tool now detects minimal data extraction and warns you:

```python
has_meaningful_data = (
    len(experience) > 0 or
    len(education) > 0 or
    len(skills) > 0 or
    about is not None
)
```

If `has_meaningful_data` is `False`, authentication likely failed.

## Common Issues

### 1. "Target page, context or browser has been closed"

**Cause**: Browser was closed prematurely (often by user pressing Ctrl+C)

**Solution**: Let the scraper complete, or re-run

### 2. Chrome is locked

**Cause**: Chrome is currently running and the cookie database is locked

**Solution**: 
- Close Chrome completely
- Use option 3 (interactive login) instead of option 4

### 3. Session expired

**Cause**: LinkedIn sessions expire after ~30 days

**Solution**: Re-authenticate using option 3

### 4. Rate limiting

**Cause**: Too many requests to LinkedIn

**Solution**: Wait a few minutes and try again

## Best Practices

1. **Authenticate once**: After initial authentication, sessions last ~30 days
2. **Don't abuse**: Avoid scraping too frequently (respect rate limits)
3. **Keep Chrome closed**: When using cookie extraction
4. **Check warnings**: The tool now warns you when data is minimal
5. **Use debug mode**: When troubleshooting, add `--debug` flag

## Still Not Working?

If you've authenticated and still get minimal data:

1. Check if you can see the full profile when logged in via browser
2. Verify the profile URL is correct
3. Check if the profile has privacy settings that restrict viewing
4. Try with your own profile first (should definitely work)
5. Check `last_scraped.html` to see what's actually being retrieved

For more details, see:
- `docs/AUTHENTICATION_GUIDE.md` - Full authentication guide
- `README.md` - General usage instructions
- GitHub Issues - Report problems

## Example: Successful Output

When authentication works correctly, you'll see data like:

```json
{
  "username": "alex-colls-outumuro",
  "name": "Alex Colls",
  "headline": "Software Engineer",
  "location": "Barcelona, Spain",
  "experience": [
    {
      "title": "Senior Engineer",
      "company": "Tech Corp",
      "duration": "Jan 2020 - Present",
      "description": "Building cool stuff..."
    }
  ],
  "education": [
    {
      "school": "University Name",
      "degree": "Computer Science",
      "years": "2015-2019"
    }
  ],
  "skills": ["Python", "JavaScript", "AWS"],
  "about": "Passionate software engineer...",
  "_metadata": {
    "sections_found": 15,
    "has_meaningful_data": true
  }
}
```

Notice:
- `sections_found: 15+` (not just 4)
- `has_meaningful_data: true`
- Arrays are populated with actual data
- `about` field has content
