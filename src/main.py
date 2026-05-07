import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from scripts.run_daily import run_pipeline
import asyncio
import pytz

def job():
    logger.info("Triggering scheduled run...")
    asyncio.run(run_pipeline(dry_run=os.getenv("DRY_RUN", "false").lower() == "true"))

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    timezone = pytz.timezone(os.getenv("TIMEZONE", "Asia/Kolkata"))
    
    # Schedule for 08:00 IST
    trigger = CronTrigger(hour=8, minute=0, timezone=timezone)
    
    scheduler.add_job(job, trigger)
    
    logger.info(f"Scheduler started. Next run at 08:00 {timezone.zone}")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
