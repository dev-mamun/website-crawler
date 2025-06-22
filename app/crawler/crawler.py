"""
Author: Md.Abdullah Al Mamun
Email: mamun1214@gmail.com
Date: 6/21/25
Year: 2025
File: crawler.py
"""

import asyncio
from urllib.parse import urljoin, urlparse
from pathlib import Path
from bs4 import BeautifulSoup
import httpx
from app.config import settings
from app.utils.logger import logger
from app.crawler.pdf_generator import PDFGenerator
from app.storage.file_storage import FileStorage


class FDICCrawler:
    def __init__(self):
        self.visited_urls = set()
        self.file_storage = FileStorage()
        self.pdf_generator = PDFGenerator()
        self.client = httpx.AsyncClient(follow_redirects=True, timeout=30.0)

    async def crawl(self, url: str, depth: int = 0):
        """Recursively crawl the website starting from the given URL"""
        if depth > settings.CRAWL_DEPTH or len(self.visited_urls) >= settings.MAX_PAGES:
            return

        if url in self.visited_urls:
            return

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
                await self.pdf_generator.generate_pdf_from_url(url, pdf_path)

                # Extract links for further crawling
                soup = BeautifulSoup(response.text, 'html.parser')
                await self.process_links(soup, url, depth)

        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")

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

        # Run tasks concurrently
        await asyncio.gather(*tasks)

    async def download_pdf(self, url: str):
        """Download a PDF file directly"""
        try:
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
