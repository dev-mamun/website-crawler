# Website Crawler

This service crawls provided website starting from the specified URL, saves HTML pages as PDFs, and downloads existing
PDFs.

## Features

- Recursive crawling of the website
- HTML pages saved as PDF with preserved formatting
- PDF downloads with standardized naming
- Scheduled crawling (default: every 12 hours)
- API endpoints for monitoring and manual triggering

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