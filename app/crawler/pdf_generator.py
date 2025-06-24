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
    # async def generate_pdf_from_url(url: str, output_path: Path):
    #     """Generate PDF from URL using Playwright"""
    #     try:
    #         async with async_playwright() as p:
    #             browser = await p.chromium.launch(headless=settings.HEADLESS)
    #             context = await browser.new_context(user_agent=settings.USER_AGENT)
    #             page = await context.new_page()
    #
    #             await page.goto(url, wait_until="networkidle")
    #
    #             # Wait for potential JavaScript rendering
    #             await asyncio.sleep(3)
    #
    #             await page.emulate_media(media="screen")
    #             await page.pdf(
    #                 path=str(output_path),
    #                 format="A4",
    #                 print_background=True,
    #                 margin={"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"}
    #             )
    #
    #             await browser.close()
    #
    #         logger.info(f"Successfully generated PDF from {url} to {output_path}")
    #         return True
    #     except Exception as e:
    #         logger.error(f"Error generating PDF from {url}: {str(e)}")
    #         return False
    class PDFGenerator:
        @staticmethod
        async def generate_pdf_from_url(url: str):
            """Generate PDF from URL with increased timeout and retries"""
            try:
                pdf_filename = PDFGenerator.get_pdf_filename(url)
                pdf_path = settings.HTML_PDF_DIR / pdf_filename

                async with async_playwright() as p:
                    # Launch browser with additional timeout options
                    browser = await p.chromium.launch(
                        headless=settings.HEADLESS,
                        timeout=settings.BROWSER_LAUNCH_TIMEOUT  # 2 minutes for browser launch
                    )
                    context = await browser.new_context(
                        user_agent=settings.USER_AGENT,
                        viewport={'width': 1280, 'height': 720}
                    )

                    page = await context.new_page()

                    # Set default navigation timeout (60 seconds)
                    page.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)
                    page.set_default_timeout(settings.DEFAULT_TIMEOUT)

                    try:
                        # Load page with extended timeout and wait conditions
                        await page.goto(
                            url,
                            timeout=settings.DEFAULT_TIMEOUT,
                            wait_until="domcontentloaded"  # Less strict than "networkidle"
                        )

                        # Wait for important elements or additional time
                        await page.wait_for_load_state("networkidle", timeout=30000)
                        await asyncio.sleep(3)  # Extra buffer time

                        # Generate PDF
                        await page.emulate_media(media="screen")
                        await page.pdf(
                            path=str(pdf_path),
                            format="A4",
                            print_background=True,
                            margin={"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"},
                            timeout=settings.PDF_GENERATION_TIMEOUT
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
