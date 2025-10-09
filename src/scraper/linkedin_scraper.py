"""LinkedIn profile scraper using Playwright."""
import asyncio
import json
import os
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page, TimeoutError


class LinkedInScraper:
    """Scrapes LinkedIn profiles using Playwright browser automation."""

    def __init__(self, headless: bool = True, debug: bool = False, session_file: Optional[str] = None):
        """Initialize the scraper.

        Args:
            headless: Run browser in headless mode
            debug: Enable debug logging
            session_file: Path to stored session/cookies file for authentication
        """
        self.headless = headless
        self.debug = debug
        self.browser: Optional[Browser] = None
        self.session_file = session_file or str(Path.home() / ".linkedin_session.json")

    async def scrape_profile(self, profile_url: str) -> str:
        """Scrape a LinkedIn profile and return the HTML content.

        Args:
            profile_url: The LinkedIn profile URL

        Returns:
            HTML content of the profile page

        Raises:
            ValueError: If the URL is invalid
            Exception: If scraping fails
        """
        if not profile_url.startswith("https://www.linkedin.com/in/"):
            raise ValueError(
                "Invalid LinkedIn profile URL. Must start with https://www.linkedin.com/in/"
            )

        async with async_playwright() as p:
            # Launch browser
            if self.debug:
                print(f"[DEBUG] Launching browser (headless={self.headless})...")

            self.browser = await p.chromium.launch(headless=self.headless)

            # Create context with realistic user agent
            context = await self.browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
            )

            # Load saved session if available
            if os.path.exists(self.session_file):
                if self.debug:
                    print(f"[DEBUG] Loading session from {self.session_file}...")
                try:
                    with open(self.session_file, 'r') as f:
                        cookies = json.load(f)
                    await context.add_cookies(cookies)
                    if self.debug:
                        print(f"[DEBUG] Loaded {len(cookies)} cookies")
                except Exception as e:
                    if self.debug:
                        print(f"[DEBUG] Failed to load session: {e}")

            page = await context.new_page()

            try:
                if self.debug:
                    print(f"[DEBUG] Navigating to {profile_url}...")

                # Navigate to profile
                await page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)

                # Wait for main content to load
                try:
                    await page.wait_for_selector(
                        "main.scaffold-layout__main", timeout=10000
                    )
                except TimeoutError:
                    if self.debug:
                        print("[DEBUG] Main content selector not found, continuing...")

                # Check if we're on auth wall
                is_auth_wall = await self._check_auth_wall(page)
                if is_auth_wall:
                    if self.debug:
                        print("[DEBUG] Auth wall detected - authentication required")
                    raise Exception(
                        "LinkedIn authentication required. Please run with --login flag first to authenticate."
                    )

                # Scroll to load lazy-loaded content
                await self._scroll_page(page)

                # Get the full HTML content
                html_content = await page.content()

                if self.debug:
                    print(f"[DEBUG] Retrieved {len(html_content)} bytes of HTML")

                # Save session for future use
                await self._save_session(context)

                return html_content

            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Error during scraping: {str(e)}")
                raise Exception(f"Failed to scrape profile: {str(e)}")

            finally:
                await context.close()
                await self.browser.close()

    async def _scroll_page(self, page: Page):
        """Scroll the page to load lazy-loaded content.

        Args:
            page: Playwright page object
        """
        try:
            # Scroll down in increments
            for i in range(5):
                await page.evaluate(f"window.scrollTo(0, {(i + 1) * 500})")
                await asyncio.sleep(0.5)

            # Scroll back to top
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)

        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error during scrolling: {str(e)}")
    
    async def _check_auth_wall(self, page: Page) -> bool:
        """Check if we're on LinkedIn auth wall.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if auth wall is detected
        """
        try:
            # Check for common auth wall indicators
            html = await page.content()
            auth_indicators = [
                'authwall',
                'checkpoint/lg/login',
                'Sign in to LinkedIn',
                'Join to view',
            ]
            return any(indicator in html for indicator in auth_indicators)
        except Exception:
            return False
    
    async def _save_session(self, context):
        """Save browser session/cookies for future use.
        
        Args:
            context: Playwright browser context
        """
        try:
            cookies = await context.cookies()
            with open(self.session_file, 'w') as f:
                json.dump(cookies, f)
            if self.debug:
                print(f"[DEBUG] Saved session to {self.session_file}")
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Failed to save session: {e}")
    
    async def login_interactive(self) -> bool:
        """Launch browser for interactive LinkedIn login.
        
        Returns:
            True if login successful
        """
        async with async_playwright() as p:
            print("\n🔐 Launching browser for LinkedIn login...")
            print("Please log in to LinkedIn in the browser window.")
            print("After logging in, close the browser window.\n")
            
            # Launch in non-headless mode
            self.browser = await p.chromium.launch(headless=False)
            
            context = await self.browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
            )
            
            page = await context.new_page()
            
            try:
                # Go to LinkedIn login
                await page.goto("https://www.linkedin.com/login")
                
                # Wait for user to login and navigate away from login page
                print("Waiting for you to log in...")
                try:
                    # Wait until we're no longer on login page
                    await page.wait_for_url(lambda url: '/login' not in url, timeout=300000)  # 5 minutes
                    print("✓ Login detected!")
                    
                    # Save the session
                    await self._save_session(context)
                    print(f"✓ Session saved to {self.session_file}")
                    print("\n✅ You can now scrape profiles with authentication!\n")
                    
                    return True
                except Exception as e:
                    print(f"\n❌ Login timeout or failed: {e}")
                    return False
                    
            finally:
                await context.close()
                await self.browser.close()
