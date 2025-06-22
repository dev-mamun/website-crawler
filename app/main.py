"""
Author: Md.Abdullah Al Mamun
Email: mamun1214@gmail.com
Date: 6/21/25
Year: 2025
File: main.py
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.logger import logger
from app.crawler.scheduler import CrawlerScheduler
from app.storage.file_storage import FileStorage

app = FastAPI(title="FDIC Website Crawler", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scheduler
scheduler = CrawlerScheduler()
file_storage = FileStorage()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up FDIC Crawler application")
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down FDIC Crawler application")
    scheduler.shutdown()


@app.get("/")
async def root():
    return {
        "message": "FDIC Website Crawler Service",
        "status": "running",
        "schedule_interval_hours": settings.SCHEDULE_INTERVAL
    }


@app.get("/pdfs")
async def list_pdfs():
    """List all stored PDFs"""
    try:
        pdfs = file_storage.list_pdfs()
        return {
            "count": len(pdfs),
            "pdfs": [str(pdf.name) for pdf in pdfs]
        }
    except Exception as e:
        logger.error(f"Error listing PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing PDFs")


@app.get("/stats")
async def get_stats():
    """Get crawler statistics"""
    try:
        return {
            "pdf_counts": file_storage.get_pdf_count(),
            "schedule_interval_hours": settings.SCHEDULE_INTERVAL
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting stats")


@app.post("/run-crawler")
async def run_crawler_now():
    """Trigger crawler manually"""
    try:
        await scheduler.run_crawler()
        return {"status": "success", "message": "Crawler executed successfully"}
    except Exception as e:
        logger.error(f"Error running crawler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
