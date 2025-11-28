"""
Browser Handler - Manages headless browser operations for fetching quiz pages
"""
import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page
import asyncio

from config import Config

logger = logging.getLogger(__name__)


class BrowserHandler:
    """Handles browser operations using Playwright for JavaScript-rendered pages"""
    
    def __init__(self, config: Config):
        self.config = config
        self.playwright = None
        self.browser: Optional[Browser] = None
        
    async def _ensure_browser(self):
        """Ensure browser is initialized"""
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.HEADLESS
            )
            logger.info("Browser initialized")
    
    async def fetch_quiz_page(self, url: str) -> Optional[str]:
        """
        Fetch and render a quiz page that may contain JavaScript
        
        Args:
            url: URL of the quiz page
            
        Returns:
            Rendered HTML content or None if failed
        """
        try:
            await self._ensure_browser()
            
            page: Page = await self.browser.new_page()
            
            # Navigate to the page
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait a bit for JavaScript to execute
            await page.wait_for_timeout(2000)
            
            # Get the rendered content
            content = await page.content()
            
            # Also get the text content for easier processing
            text_content = await page.inner_text("body")
            
            await page.close()
            
            logger.info(f"Successfully fetched quiz page from {url}")
            return text_content  # Return text content which is easier to parse
            
        except Exception as e:
            logger.error(f"Error fetching quiz page: {str(e)}", exc_info=True)
            return None
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
