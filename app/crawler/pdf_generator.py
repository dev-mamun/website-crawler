"""
Author: Md.Abdullah Al Mamun
Email: mamun1214@gmail.com
Date: 6/21/25
Year: 2025
File: pdf_generator.py
"""

import asyncio
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from app.config import settings
from app.utils.logger import logger


class PDFGenerator:
    @staticmethod
    async def generate_pdf_from_url(url: str, output_path: Path):
        """Generate PDF from URL using Playwright"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=settings.HEADLESS)
                context = await browser.new_context(user_agent=settings.USER_AGENT)
                page = await context.new_page()

                await page.goto(url, wait_until="networkidle")

                # Wait for potential JavaScript rendering
                await asyncio.sleep(2)

                await page.emulate_media(media="screen")
                await page.pdf(
                    path=str(output_path),
                    format="A4",
                    print_background=True,
                    margin={"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"}
                )

                await browser.close()

            logger.info(f"Successfully generated PDF from {url} to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error generating PDF from {url}: {str(e)}")
            return False

    @staticmethod
    def get_pdf_filename(url: str) -> str:
        """Generate standardized PDF filename from URL in format domain_path_timestamp.pdf"""
        # Remove protocol and www.
        clean_url = re.sub(r"^https?://(www\.)?", "", url)

        # Extract full domain (e.g., "fdic.gov")
        domain = clean_url.split("/")[0]  # Takes "fdic.gov"

        # Extract path and replace slashes/special chars with underscores
        path_segments = clean_url.split("/")[1:] or ["index"]  # Fallback to "index" if no path
        path = "_".join(segment for segment in path_segments if segment)  # Skip empty segments

        # Sanitize path (keep alphanumeric, hyphens, underscores)
        path = re.sub(r"[^\w-]", "_", path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{domain}_{path}_{timestamp}.pdf"
