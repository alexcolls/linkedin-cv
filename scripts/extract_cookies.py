#!/usr/bin/env python3
"""Extract LinkedIn cookies from Chrome SQLite database."""
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path


def extract_linkedin_cookies():
    """Extract LinkedIn cookies from Chrome."""
    # Chrome cookies database
    chrome_cookies = Path.home() / ".config" / "google-chrome" / "Default" / "Cookies"
    
    if not chrome_cookies.exists():
        print(f"❌ Chrome cookies database not found at: {chrome_cookies}")
        return None
    
    # Create temp copy (Chrome locks the database)
    temp_cookies = "/tmp/chrome_cookies_copy"
    try:
        shutil.copy2(chrome_cookies, temp_cookies)
    except Exception as e:
        print(f"❌ Failed to copy cookies database: {e}")
        print("💡 Try closing Chrome first")
        return None
    
    try:
        # Connect to database
        conn = sqlite3.connect(temp_cookies)
        cursor = conn.cursor()
        
        # Query LinkedIn cookies
        cursor.execute("""
            SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, samesite
            FROM cookies
            WHERE host_key LIKE '%linkedin.com%'
        """)
        
        cookies = []
        for row in cursor.fetchall():
            name, value, domain, path, expires, secure, httponly, samesite = row
            
            cookie = {
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
                "expires": expires / 1000000 - 11644473600 if expires > 0 else -1,  # Convert Chrome time to Unix
                "httpOnly": bool(httponly),
                "secure": bool(secure),
                "sameSite": ["None", "Lax", "Strict"][samesite] if samesite in [0, 1, 2] else "None"
            }
            cookies.append(cookie)
        
        conn.close()
        os.remove(temp_cookies)
        
        return cookies
        
    except Exception as e:
        print(f"❌ Error extracting cookies: {e}")
        if os.path.exists(temp_cookies):
            os.remove(temp_cookies)
        return None


def main():
    """Main function."""
    print("🔍 Extracting LinkedIn cookies from Chrome...")
    
    cookies = extract_linkedin_cookies()
    
    if not cookies:
        print("\n❌ Failed to extract cookies")
        print("\n💡 Try:")
        print("   1. Close Chrome completely")
        print("   2. Run this script again")
        print("   3. Or log in using: poetry run python -m src.cli --login")
        sys.exit(1)
    
    print(f"✅ Found {len(cookies)} LinkedIn cookies")
    
    # Save to session file
    session_file = Path.home() / ".linkedin_session.json"
    with open(session_file, 'w') as f:
        json.dump(cookies, f, indent=2)
    
    print(f"✅ Saved to: {session_file}")
    print("\n🎉 You can now run: poetry run python -m src.cli alex-colls-outumuro")


if __name__ == "__main__":
    main()
