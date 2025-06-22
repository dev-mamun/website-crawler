"""
Author: Md.Abdullah Al Mamun
Email: mamun1214@gmail.com
Date: 6/21/25
Year: 2025
File: scheduler.py
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings
from app.utils.logger import logger
from app.crawler.crawler import FDICCrawler


class CrawlerScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.crawler = FDICCrawler()

    async def run_crawler(self):
        """Run the crawler task"""
        logger.info("Starting scheduled crawl job")
        try:
            await self.crawler.crawl(settings.BASE_URL)
            logger.info("Crawl job completed successfully")
        except Exception as e:
            logger.error(f"Crawl job failed: {str(e)}")
        finally:
            await self.crawler.close()

    def start(self):
        """Start the scheduler"""
        trigger = IntervalTrigger(hours=settings.SCHEDULE_INTERVAL)
        self.scheduler.add_job(
            self.run_crawler,
            trigger=trigger,
            max_instances=1
        )
        self.scheduler.start()
        logger.info(f"Scheduler started with interval: every {settings.SCHEDULE_INTERVAL} hours")

    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown")
