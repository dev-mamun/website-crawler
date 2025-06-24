"""
Author: Md.Abdullah Al Mamun
Email: mamun1214@gmail.com
Date: 6/21/25
Year: 2025
File: config.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    # Crawler settings
    BASE_URL = str(os.getenv("BASE_URL", "https://www.fdic.gov/risk-management-manual-examination-policies"))
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    CRAWL_DEPTH = int(os.getenv("CRAWL_DEPTH", 3))
    MAX_PAGES = int(os.getenv("MAX_PAGES", 50))  # Limit for demo purposes

    # Storage settings
    HTML_PDF_DIR = BASE_DIR / "storage/html_pdfs"
    DOWNLOADED_PDF_DIR = BASE_DIR / "storage/downloaded_pdfs"

    # Scheduling settings
    SCHEDULE_INTERVAL = int(os.getenv("SCHEDULE_INTERVAL", 12))  # hours between crawls

    # Playwright settings
    HEADLESS = True

    # Database settings
    DATABASE_URL = "sqlite:///./crawl_jobs.db"

    # Make BASE_DIR available as a setting
    BASE_DIR = BASE_DIR
    # Add static files configuration
    STATIC_URL = "/static"
    STATIC_ROOT = BASE_DIR / "storage"
    CRAWL_DELAY = float(os.getenv("CRAWL_DELAY", 0.1))  # 500 milliseconds delay
    STORAGE_PATH = str(os.getenv("STORAGE_PATH", "./storage"))
    DEBUG = bool(os.getenv("DEBUG", False))
    SCHEDULED = bool(os.getenv("SCHEDULED", False))
    # Timeout settings (in milliseconds)
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", 60000))  # 1 minute
    BROWSER_LAUNCH_TIMEOUT = int(os.getenv("BROWSER_LAUNCH_TIMEOUT", 120000))  # 2 minutes
    NAVIGATION_TIMEOUT = int(os.getenv("NAVIGATION_TIMEOUT", 60000))  # 1 minute
    PDF_GENERATION_TIMEOUT = int(os.getenv("PDF_GENERATION_TIMEOUT", 60000))  # 1 minute
    # Resource control
    MAX_PDF_GENERATION_ATTEMPTS = int(os.getenv("MAX_PDF_GENERATION_ATTEMPTS", 5))
    PDF_FILENAME_MAX_LENGTH = int(os.getenv("PDF_FILENAME_MAX_LENGTH", 120))
    # Cleanup Settings
    PDF_RETENTION_DAYS = int(os.getenv("PDF_RETENTION_DAYS", 7))


settings = Settings()

# Create directories if they don't exist
settings.HTML_PDF_DIR.mkdir(parents=True, exist_ok=True)
settings.DOWNLOADED_PDF_DIR.mkdir(parents=True, exist_ok=True)
