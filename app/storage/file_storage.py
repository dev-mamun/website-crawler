"""
Author: Md.Abdullah Al Mamun
Email: mamun1214@gmail.com
Date: 6/21/25
Year: 2025
File: file_storage.py
"""

from pathlib import Path
from typing import List, Dict
from app.config import settings
from app.utils.logger import logger
from fastapi import Request


class FileStorage:

    def list_pdfs(self, request: Request = None) -> List[Dict[str, str]]:
        """List all PDF files with full URLs"""
        pdfs = []

        # HTML PDFs
        for pdf in settings.HTML_PDF_DIR.glob("*.pdf"):
            pdfs.append({
                "name": pdf.name,
                "path": str(pdf.relative_to(settings.BASE_DIR)),
                "type": "html_pdf",
                "url": str(request.base_url) + f"static/html_pdfs/{pdf.name}" if request else None
            })

        # Downloaded PDFs
        for pdf in settings.DOWNLOADED_PDF_DIR.glob("*.pdf"):
            pdfs.append({
                "name": pdf.name,
                "path": str(pdf.relative_to(settings.BASE_DIR)),
                "type": "downloaded_pdf",
                "url": str(request.base_url) + f"static/downloaded_pdfs/{pdf.name}" if request else None
            })

        return sorted(pdfs, key=lambda x: x['name'])

    def get_pdf_count(self) -> dict:
        """Get count of PDFs by type"""
        return {
            "html_pdfs": len(list(settings.HTML_PDF_DIR.glob("*.pdf"))),
            "downloaded_pdfs": len(list(settings.DOWNLOADED_PDF_DIR.glob("*.pdf")))
        }

    def cleanup_old_files(self, days_old: int = 30):
        """Clean up files older than specified days"""
        # Implementation would go here
        pass
