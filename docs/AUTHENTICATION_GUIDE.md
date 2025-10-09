# 🔐 LinkedIn Authentication Guide

## Why Authentication is Needed

LinkedIn **masks** profile content (job descriptions, skills, etc.) when accessed without authentication. You'll see asterisks (`*****`) instead of actual text.

**Without auth:** `***** ** * ** ** ********* **** ****** *** ** ********`  
**With auth:** `Quami is a 3D AI assistant that allows you to interact with your voice...`

## How It Works

The tool uses **persistent browser sessions** (cookies) to maintain authentication:

1. You log in **once** using your real LinkedIn credentials
2. Session cookies are saved to `~/.linkedin_session.json`
3. Future scrapes reuse these cookies automatically
4. No need to log in again until session expires

## 🚀 Quick Start

### Method 1: Interactive Menu

```bash
./run.sh
```

Then select option **2) 🔐 Login to LinkedIn**

### Method 2: Command Line

```bash
python -m src.cli --login
```

Or with Poetry:

```bash
poetry run python -m src.cli --login
```

## Step-by-Step Login Process

1. **Run the login command** (see above)

2. **Browser opens** - A Chrome/Chromium window will launch

3. **Log in to LinkedIn** - Use your normal LinkedIn credentials
   - Enter your email/username
   - Enter your password  
   - Complete any 2FA if required
   - Wait for LinkedIn homepage to load

4. **Session saved** - Once logged in, close the browser
   - Session automatically saved to `~/.linkedin_session.json`
   - You'll see: ✅ You can now scrape profiles with authentication!

5. **Generate CVs** - Now run CV generation normally:
   ```bash
   python -m src.cli alex-colls-outumuro
   ```

## 🔒 Security & Privacy

### What is Stored?

- **Session cookies only** - Saved to `~/.linkedin_session.json`
- **No credentials** - Your password is NEVER stored
- **Local only** - Cookies stay on your machine

### Cookie File Location

```bash
~/.linkedin_session.json
```

Example (anonymized):
```json
[
  {
    "name": "li_at",
    "value": "AQEDATxxxxxx...",
    "domain": ".linkedin.com",
    "path": "/"
  },
  ...
]
```

### Security Best Practices

✅ **Safe:**
- Using on your personal development machine
- The session file is only readable by your user

⚠️ **Be careful:**
- Don't commit `.linkedin_session.json` to git
- Don't share the session file
- Don't use on shared/public computers

🛡️ **Extra security:**
- Add to `.gitignore` (already done)
- Set restrictive permissions: `chmod 600 ~/.linkedin_session.json`
- Delete when done: `rm ~/.linkedin_session.json`

## Session Expiration

LinkedIn sessions typically expire after:
- **~30 days** of inactivity
- When you log out from LinkedIn
- When LinkedIn detects suspicious activity

**What happens when expired?**
- You'll see auth wall error
- Simply run `--login` again to refresh

## Troubleshooting

### Problem: "Auth wall detected"

**Solution:** Your session expired. Log in again:
```bash
python -m src.cli --login
```

### Problem: Browser doesn't open

**Causes:**
- Missing display (SSH without X forwarding)
- Playwright browser not installed

**Solution:**
```bash
poetry run playwright install chromium
```

### Problem: "Failed to load session"

**Causes:**
- Corrupted session file
- Invalid JSON

**Solution:** Delete and recreate:
```bash
rm ~/.linkedin_session.json
python -m src.cli --login
```

### Problem: Login page keeps refreshing

**Causes:**
- LinkedIn detecting automation
- Need to verify via email/SMS

**Solution:**
- Complete the verification in the browser
- LinkedIn may require you to verify it's really you

### Problem: Still seeing masked content

**Causes:**
- Session not properly saved
- Profile is very private

**Solution:**
```bash
# Try login again
python -m src.cli --login --debug

# Check session file exists
ls -la ~/.linkedin_session.json

# Try with visible browser
python -m src.cli alex-colls-outumuro --no-headless --debug
```

## Advanced Usage

### Custom Session File Location

```bash
# Set custom location
export LINKEDIN_SESSION_FILE="/path/to/my/session.json"

# Or pass directly (code modification needed)
```

### Headless vs Non-Headless

**Login** - Always non-headless (you need to interact)
```bash
python -m src.cli --login
```

**Scraping** - Can be headless (no interaction needed)
```bash
# Headless (default)
python -m src.cli username

# Non-headless (see what's happening)
python -m src.cli username --no-headless
```

### Debug Mode

See what's happening:
```bash
python -m src.cli --login --debug
python -m src.cli username --debug
```

## FAQs

### Q: Is this against LinkedIn's ToS?

**A:** LinkedIn's ToS prohibits automated data collection. This tool is for **personal use** to create your own CV. Use responsibly.

### Q: Will LinkedIn ban my account?

**A:** Unlikely for personal use, but:
- Don't scrape hundreds of profiles
- Don't run constantly
- Don't sell/share scraped data
- Use rate limiting

### Q: Can I use this for my team/company?

**A:** Each person should authenticate with their own account. Don't share session files.

### Q: Do I need LinkedIn Premium?

**A:** No, works with free accounts.

### Q: What if I have 2FA enabled?

**A:** Complete 2FA in the browser during login. Session will be saved after verification.

### Q: How long does login take?

**A:** 30-60 seconds (you need to manually log in once)

### Q: Can I automate the login?

**A:** No - LinkedIn's security requires manual interaction. You only need to do it once though!

## Best Practices

1. **Login once** - Session lasts ~30 days
2. **Check session file** - Verify `~/.linkedin_session.json` exists
3. **Test with your profile first** - Make sure it works
4. **Use rate limiting** - Don't scrape too fast
5. **Keep cookies secure** - Don't share session file
6. **Logout when done** - Remove session file if not using regularly

## Example Workflow

```bash
# 1. First time setup
poetry install
poetry run playwright install chromium

# 2. Authenticate (once)
./run.sh  # Select option 2
# Or: poetry run python -m src.cli --login

# 3. Generate your CV
poetry run python -m src.cli alex-colls-outumuro

# 4. Generate for different profile
poetry run python -m src.cli another-username

# 5. Session expired? Re-authenticate
poetry run python -m src.cli --login
```

## Summary

✅ **Benefits of Authentication:**
- Access full profile content (no masked text)
- Better descriptions and details
- More reliable scraping
- Reusable session (~30 days)

⚠️ **Things to Remember:**
- Login required once per month
- Credentials never stored
- Session cookies saved locally
- Use responsibly

🚀 **Ready to start?**

```bash
./run.sh
# Select: 2) 🔐 Login to LinkedIn
```

---

**Need Help?**

- Check [GitHub Issues](https://github.com/alexcolls/linkedin-cv/issues)
- Read [README.md](../README.md)
- Enable `--debug` flag for troubleshooting
