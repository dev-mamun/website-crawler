"""
Author: Md.Abdullah Al Mamun
Email: mamun1214@gmail.com
Date: 6/21/25
Year: 2025
File: file_storage.py
"""

from pathlib import Path
from typing import List
from app.config import settings
from app.utils.logger import logger


class FileStorage:
    def list_pdfs(self) -> List[Path]:
        """List all PDF files in storage"""
        html_pdfs = list(settings.HTML_PDF_DIR.glob("*.pdf"))
        downloaded_pdfs = list(settings.DOWNLOADED_PDF_DIR.glob("*.pdf"))
        return html_pdfs + downloaded_pdfs

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
