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
    @classmethod
    async def generate_pdf_with_retry(
            cls,
            url: str,
            max_retries: int = settings.MAX_PDF_GENERATION_ATTEMPTS
    ) -> Optional[Path]:
        """
        Generate PDF with automatic retries and exponential backoff
        Args:
            url: URL to generate PDF from
            max_retries: Maximum number of retry attempts
        Returns:
            Path to generated PDF or None if all attempts fail
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} for {url}")
                result = await cls.generate_pdf_from_url(url)
                if result:
                    return result
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} attempts for {url}: {str(e)}")
                    return None
                wait_time = 5 * (attempt + 1)
                logger.warning(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        return None

    @staticmethod
    async def generate_pdf_from_url(url: str) -> Optional[Path]:
        """
        Generate PDF from URL with enhanced stability features
        Args:
            url: URL to generate PDF from
        Returns:
            Path to generated PDF or None if generation fails
        """
        try:
            pdf_filename = PDFGenerator.get_pdf_filename(url)
            pdf_path = settings.HTML_PDF_DIR / pdf_filename

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=settings.HEADLESS,
                    timeout=settings.BROWSER_LAUNCH_TIMEOUT,
                    args=[
                        '--disable-gpu',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--single-process'
                    ]
                )

                context = await browser.new_context(
                    user_agent=settings.USER_AGENT,
                    viewport={'width': 1280, 'height': 720},
                    java_script_enabled=True,
                    bypass_csp=False,
                    ignore_https_errors=True
                )

                try:
                    page = await context.new_page()

                    # Configure timeouts
                    page.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)
                    page.set_default_timeout(settings.DEFAULT_TIMEOUT)

                    # Optimize requests
                    await page.route(re.compile(r'\.(png|jpg|jpeg|gif|webp|css)$'),
                                     lambda route: route.abort())

                    # Multi-stage loading with fallbacks
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    except:
                        await page.goto(url, wait_until="load", timeout=30000)

                    # Stability checks
                    await page.wait_for_function(
                        """() => document.readyState === 'complete'""",
                        timeout=15000
                    )

                    # Generate PDF with additional checks
                    try:
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
                    except Exception as pdf_error:
                        logger.warning(f"PDF generation failed, attempting screenshot: {str(pdf_error)}")
                        screenshot_path = pdf_path.with_suffix('.png')
                        await page.screenshot(path=str(screenshot_path), full_page=True)
                        logger.info(f"Saved screenshot instead: {screenshot_path}")
                        return screenshot_path

                finally:
                    await context.close()
                    await browser.close()

        except Exception as e:
            logger.error(f"PDF generation failed for {url}: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def get_pdf_filename(url: str, max_length: int = settings.PDF_FILENAME_MAX_LENGTH) -> str:
        """
        Generate standardized PDF filename with safe character handling
        Args:
            url: URL to convert to filename
            max_length: Maximum allowed filename length
        Returns:
            Safe filename string
        """
        try:
            # Basic sanitization
            clean_url = re.sub(r"^https?://(www\.)?", "", url.lower())
            domain = clean_url.split("/")[0].split(":")[0]  # Remove port if present

            # Process path segments
            path_segments = clean_url.split("/")[1:] or ["index"]
            path = "_".join(
                re.sub(r"[^\w-]", "_", segment)[:20]  # Truncate and sanitize each segment
                for segment in path_segments
                if segment.strip()
            )[:50]  # Limit total path length

            # Final sanitization
            safe_domain = re.sub(r"[^\w-]", "_", domain)
            safe_path = re.sub(r"_+", "_", path).strip("_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            filename = f"{safe_domain}_{safe_path}_{timestamp}.pdf"

            # Ensure filesystem-safe length
            return filename[:max_length] if len(filename) > max_length else filename

        except Exception as e:
            logger.error(f"Filename generation failed for {url}: {str(e)}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"document_{timestamp}.pdf"

    @staticmethod
    async def cleanup_old_files(days_old: int = 30) -> None:
        """
        Clean up files older than specified days
        Args:
            days_old: Delete files older than this many days
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 86400)
            for pdf_dir in [settings.HTML_PDF_DIR, settings.DOWNLOADED_PDF_DIR]:
                for file in pdf_dir.glob("*"):
                    if file.stat().st_mtime < cutoff_time:
                        file.unlink()
                        logger.info(f"Deleted old file: {file}")
        except Exception as e:
            logger.error(f"File cleanup failed: {str(e)}")
