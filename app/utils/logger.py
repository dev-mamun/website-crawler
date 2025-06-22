"""
Author: Md.Abdullah Al Mamun
Email: mamun1214@gmail.com
Date: 6/21/25
Year: 2025
File: logger.py
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import settings


def setup_logger():
    # Use the BASE_DIR from settings
    log_dir = settings.BASE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("crawler")
    logger.setLevel(logging.INFO)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_dir / "crawler.log",
        maxBytes=1024 * 1024 * 5,  # 5MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)s - %(message)s"
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
