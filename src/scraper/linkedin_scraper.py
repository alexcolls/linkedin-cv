"""LinkedIn profile scraper using Playwright."""
import asyncio
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page, TimeoutError


class LinkedInScraper:
    """Scrapes LinkedIn profiles using Playwright browser automation."""

    def __init__(self, headless: bool = True, debug: bool = False):
        """Initialize the scraper.

        Args:
            headless: Run browser in headless mode
            debug: Enable debug logging
        """
        self.headless = headless
        self.debug = debug
        self.browser: Optional[Browser] = None

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
                viewport={"width": 1920, "height": 1080"},
                locale="en-US",
            )

            page = await context.new_page()

            try:
                if self.debug:
                    print(f"[DEBUG] Navigating to {profile_url}...")

                # Navigate to profile
                await page.goto(profile_url, wait_until="networkidle", timeout=30000)

                # Wait for main content to load
                try:
                    await page.wait_for_selector(
                        "main.scaffold-layout__main", timeout=10000
                    )
                except TimeoutError:
                    if self.debug:
                        print("[DEBUG] Main content selector not found, continuing...")

                # Scroll to load lazy-loaded content
                await self._scroll_page(page)

                # Get the full HTML content
                html_content = await page.content()

                if self.debug:
                    print(f"[DEBUG] Retrieved {len(html_content)} bytes of HTML")

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
