"""
Author: Md.Abdullah Al Mamun
Email: mamun1214@gmail.com
Date: 6/21/25
Year: 2025
File: crawler.py
"""

import asyncio
import httpx
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from app.config import settings
from app.utils.logger import logger
from app.crawler.pdf_generator import PDFGenerator
from app.storage.file_storage import FileStorage
from time import perf_counter


class FDICCrawler:
    def __init__(self):
        self.visited_urls = set()
        self.file_storage = FileStorage()
        self.pdf_generator = PDFGenerator()
        self.client = httpx.AsyncClient(follow_redirects=True, timeout=60.0)
        self.last_request_time = 0

    async def crawl(self, url: str, depth: int = 0):
        """Recursively crawl the website starting from the given URL"""
        if depth > settings.CRAWL_DEPTH or len(self.visited_urls) >= settings.MAX_PAGES:
            return

        if url in self.visited_urls:
            return

        # Enforce delay between requests
        await self._enforce_delay()

        self.visited_urls.add(url)
        logger.info(f"Crawling {url} (depth {depth})")

        try:
            # Check if URL is PDF
            if url.lower().endswith('.pdf'):
                await self.download_pdf(url)
                return

            # Process HTML page
            response = await self.client.get(url)
            response.raise_for_status()

            if 'text/html' in response.headers.get('content-type', ''):
                # Save HTML as PDF
                pdf_filename = self.pdf_generator.get_pdf_filename(url)
                pdf_path = settings.HTML_PDF_DIR / pdf_filename
                await self.pdf_generator.generate_pdf_from_url(url)

                # Extract links for further crawling
                soup = BeautifulSoup(response.text, 'html.parser')
                await self.process_links(soup, url, depth)

        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")

    async def _enforce_delay(self):
        """Enforce delay between requests to be polite to the server"""
        elapsed = perf_counter() - self.last_request_time
        if elapsed < settings.CRAWL_DELAY:
            wait_time = settings.CRAWL_DELAY - elapsed
            logger.debug(f"Waiting {wait_time:.2f} seconds before next request")
            await asyncio.sleep(wait_time)
        self.last_request_time = perf_counter()

    async def process_links(self, soup: BeautifulSoup, base_url: str, depth: int):
        """Process all links found on the page"""
        tasks = []
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Skip non-HTTP links and anchors
            if href.startswith('#') or href.startswith('mailto:'):
                continue

            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)

            # Ensure we stay on the same domain
            if urlparse(absolute_url).netloc != urlparse(base_url).netloc:
                continue

            # Schedule crawling for the next depth
            tasks.append(self.crawl(absolute_url, depth + 1))

        # Run tasks concurrently but with rate limiting
        for task in tasks:
            await task
            await asyncio.sleep(settings.CRAWL_DELAY)

    async def download_pdf(self, url: str):
        """Download a PDF file directly"""
        try:
            # Enforce delay before PDF download
            await self._enforce_delay()

            pdf_filename = self.pdf_generator.get_pdf_filename(url)
            pdf_path = settings.DOWNLOADED_PDF_DIR / pdf_filename

            async with self.client.stream('GET', url) as response:
                response.raise_for_status()
                with open(pdf_path, 'wb') as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)

            logger.info(f"Downloaded PDF: {url} -> {pdf_path}")
        except Exception as e:
            logger.error(f"Error downloading PDF {url}: {str(e)}")

    async def close(self):
        """Clean up resources"""
        await self.client.aclose()
