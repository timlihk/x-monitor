from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud, schemas
from app.services.twitter_service import TwitterService
from app.services.llm_service import LLMService
from app.config import Config
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.twitter_service = TwitterService()
        self.llm_service = LLMService()
    
    def start(self):
        self.scheduler.add_job(
            self.run_daily_job,
            CronTrigger(
                hour=Config.DAILY_RUN_HOUR,
                minute=Config.DAILY_RUN_MINUTE,
                timezone=Config.SCHEDULER_TIMEZONE
            ),
            id='daily_tweet_summary',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info(f"Scheduler started. Daily job will run at {Config.DAILY_RUN_HOUR}:{Config.DAILY_RUN_MINUTE:02d} {Config.SCHEDULER_TIMEZONE}")
    
    def shutdown(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def run_daily_job(self):
        logger.info("Starting daily tweet monitoring job")
        db: Session = SessionLocal()
        
        try:
            active_terms = crud.get_active_monitored_terms(db)
            logger.info(f"Processing {len(active_terms)} active terms")
            
            for term in active_terms:
                await self.process_term(db, term)
                
        except Exception as e:
            logger.error(f"Error in daily job: {str(e)}")
        finally:
            db.close()
            logger.info("Daily job completed")
    
    async def process_term(self, db: Session, term):
        try:
            logger.info(f"Processing term: {term.keyword}")
            
            tweets = await self.twitter_service.search_tweets(
                keyword=term.keyword,
                restrict_following=term.restrict_following,
                max_results=50
            )
            
            if not tweets:
                logger.info(f"No tweets found for {term.keyword}")
                return
            
            summary = await self.llm_service.summarize_tweets(tweets, term.keyword)
            
            result_data = schemas.ResultCreate(
                keyword_id=term.id,
                tweets_raw=tweets,
                summary=summary
            )
            
            crud.create_result(db=db, result=result_data)
            logger.info(f"Processed {len(tweets)} tweets for {term.keyword}")
            
        except Exception as e:
            logger.error(f"Error processing term {term.keyword}: {str(e)}")
    
    async def run_manual_job(self):
        logger.info("Starting manual job")
        await self.run_daily_job()