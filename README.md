# Website Crawler

This service crawls the FDIC website starting from the specified URL, saves HTML pages as PDFs, and downloads existing
PDFs.

## Features

- Recursive crawling of the FDIC website
- HTML pages saved as PDF with preserved formatting
- PDF downloads with standardized naming
- Scheduled crawling (default: every 12 hours)
- API endpoints for monitoring and manual triggering

## Project Structure

      website-crawler/
      ├── app/ # Application source code
      │ ├── init.py # Python package marker
      │ ├── main.py # FastAPI application setup
      │ ├── config.py # Configuration settings
      │ ├── crawler/ # Crawler module
      │ │ ├── init.py
      │ │ ├── crawler.py # Main crawling logic
      │ │ ├── pdf_generator.py # PDF generation with Playwright
      │ │ └── scheduler.py # APScheduler setup
      │ ├── models/ # Database models
      │ │ ├── init.py
      │ │ └── crawl_job.py # Job tracking model
      │ ├── storage/ # Storage handling
      │ │ ├── init.py
      │ │ └── file_storage.py # File operations
      │ └── utils/ # Utility functions
      │ ├── init.py
      │ ├── logger.py # Logging configuration
      │ └── helpers.py # Helper functions
      ├── tests/ # Test files
      │ ├── init.py
      │ └── test_crawler.py
      ├── storage/ # PDF storage (auto-created)
      │ ├── html_pdfs/ # HTML-to-PDF conversions
      │ └── downloaded_pdfs/ # Direct PDF downloads
      ├── Pipfile # Pipenv dependencies
      ├── Pipfile.lock
      ├── README.md # This documentation
      ├── .env # Environment variables
      └── .gitignore # Git ignore rules

### Key Directories Explained:

1. **app/** - Core application logic:
    - 🐍`main.py`: FastAPI application entry point
    - 🐍`config.py`: Centralized configuration
    - 📁`crawler/`: Website crawling and PDF generation
    - 📁`models/`: Database models (if using DB)
    - 📁`storage/`: File handling operations
    - 📁`utils/`: Common utilities

2. **📁 storage/** - Auto-created directories:
    - 📁`html_pdfs/`: Stores converted HTML pages as PDFs
    - 📁`downloaded_pdfs/`: Stores directly downloaded PDFs

3. **Root Files**:
    - `Pipfile`: Python dependency management
    - `.env`: Environment configuration
    - `.gitignore`: Version control exclusions

## Setup

1. **Prerequisites**:
    - Python 3.9+
    - Node.js (for Playwright)
    - pipenv

2. **Install dependencies**:
   ```bash
   pipenv install
   pipenv run playwright install
   pipenv run playwright install-deps

3. **Run Application**:
   ```bash   
   pipenv shell
   uvicorn app.main:app --reload
