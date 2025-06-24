"""
Author: Md.Abdullah Al Mamun
Email: mamun1214@gmail.com
Date: 6/21/25
Year: 2025
File: pdf_generator.py
Updated with enhanced error handling, resource control, and filename management
"""

import asyncio
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Union
from playwright.async_api import async_playwright
from app.config import settings
from app.utils.logger import logger


class PDFGenerator:
    @staticmethod
    async def generate_pdf_from_url(url: str) -> Optional[Path]:
        """Generate PDF from URL with proper static method implementation"""
        try:
            pdf_filename = PDFGenerator.get_pdf_filename(url)
            pdf_path = settings.HTML_PDF_DIR / pdf_filename

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=settings.HEADLESS,
                    timeout=settings.BROWSER_LAUNCH_TIMEOUT
                )
                context = await browser.new_context(
                    user_agent=settings.USER_AGENT,
                    viewport={'width': 1280, 'height': 720}
                )

                page = await context.new_page()
                page.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)
                page.set_default_timeout(settings.DEFAULT_TIMEOUT)

                try:
                    await page.goto(
                        url,
                        timeout=settings.DEFAULT_TIMEOUT,
                        wait_until="domcontentloaded"
                    )
                    await page.wait_for_load_state("networkidle", timeout=30000)
                    await asyncio.sleep(3)

                    await page.emulate_media(media="screen")
                    await page.pdf(
                        path=str(pdf_path),
                        format="A4",
                        print_background=True,
                        margin={"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"}
                    )

                    logger.info(f"Successfully generated PDF: {pdf_path}")
                    return pdf_path

                except Exception as e:
                    logger.error(f"Error during page processing for {url}: {str(e)}")
                    return None

                finally:
                    await browser.close()

        except Exception as e:
            logger.error(f"Browser setup failed for {url}: {str(e)}")
            return None

    @staticmethod
    def get_pdf_filename(url: str) -> str:
        """Generate standardized PDF filename"""
        clean_url = re.sub(r"^https?://(www\.)?", "", url)
        domain = clean_url.split("/")[0]
        path_segments = clean_url.split("/")[1:] or ["index"]
        path = "_".join(segment for segment in path_segments if segment)
        path = re.sub(r"[^\w-]", "_", path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{domain}_{path}_{timestamp}.pdf"

    @classmethod
    async def generate_pdf_with_retry(cls, url: str, max_retries: int = 2):
        """Retry wrapper with proper class method reference"""
        for attempt in range(max_retries):
            try:
                return await cls.generate_pdf_from_url(url)  # Correct static method call
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(5 * (attempt + 1))
