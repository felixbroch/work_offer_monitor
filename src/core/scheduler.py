#!/usr/bin/env python3
"""
Job Search Scheduler

This module handles automatic scheduling of job searches using APScheduler.
It runs daily job monitoring tasks and integrates with the job tracking system.
"""

import logging
import sys
import time
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from .job_search_engine import JobSearchEngine
from .database import JobDatabase
from .history_tracker import JobHistoryTracker
from config.config import OPENAI_SETTINGS, SCHEDULER_SETTINGS, FILES


class JobSearchScheduler:
    """
    Scheduler for automatic job search monitoring.
    
    This class handles the scheduling of daily job searches, integrates with
    the job tracking system, and manages reporting.
    """
    
    def __init__(self, api_key: str, db_path: Optional[str] = None):
        """
        Initialize the job search scheduler.
        
        Args:
            api_key (str): OpenAI API key for job search
            db_path (Optional[str]): Path to SQLite database file
        """
        self.api_key = api_key
        self.db_path = db_path or FILES.get("database", "job_history.db")
        
        # Initialize components
        self.db = JobDatabase(self.db_path)
        self.tracker = JobHistoryTracker(self.db)
        self.search_engine = JobSearchEngine(api_key)
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize scheduler
        self.scheduler = BlockingScheduler()
        self._setup_scheduler_events()
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('job_monitor.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def _setup_scheduler_events(self):
        """Set up scheduler event handlers."""
        self.scheduler.add_listener(self._on_job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._on_job_error, EVENT_JOB_ERROR)
    
    def _on_job_executed(self, event):
        """Handle successful job execution."""
        self.logger.info(f"Scheduled job executed successfully: {event.job_id}")
    
    def _on_job_error(self, event):
        """Handle job execution errors."""
        self.logger.error(f"Scheduled job failed: {event.job_id}, Exception: {event.exception}")
    
    def run_daily_monitoring(self):
        """
        Execute the daily job monitoring task.
        
        This method:
        1. Loads companies to monitor
        2. Searches for jobs at each company
        3. Processes results through the history tracker
        4. Generates daily reports
        5. Performs weekly cleanup
        """
        try:
            self.logger.info("Starting daily job monitoring...")
            
            # Load companies to monitor
            companies = self.search_engine.load_companies()
            self.logger.info(f"Monitoring {len(companies)} companies")
            
            # Process each company
            for company in companies:
                try:
                    self.logger.info(f"Processing {company['company_name']}...")
                    
                    # Search for jobs using web search
                    search_result = self.search_engine.search_company_jobs(
                        company['company_name'],
                        company['career_page_url']
                    )
                    
                    # Extract structured job data from search results
                    job_data_list = self.search_engine.extract_structured_jobs(
                        search_result, 
                        company['company_name']
                    )
                    
                    # Process jobs through history tracker
                    summary = self.tracker.process_company_jobs(
                        company['company_name'], 
                        job_data_list
                    )
                    
                    self.logger.info(f"Processed {company['company_name']}: {summary}")
                    
                    # Small delay between companies
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {company['company_name']}: {e}")
            
            # Generate and save daily report
            self._generate_daily_report()
            
            # Perform weekly cleanup on Mondays
            if datetime.now().weekday() == 0:
                self.logger.info("Performing weekly cleanup...")
                self.tracker.cleanup_old_data()
            
            self.logger.info("Daily job monitoring completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in daily job monitoring: {e}")
    
    def _generate_daily_report(self):
        """Generate and save daily status report."""
        try:
            report = self.tracker.generate_status_report()
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y-%m-%d")
            filename = f"daily_report_{timestamp}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info(f"Daily report saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")
    
    def start_scheduler(self):
        """
        Start the scheduler with daily job monitoring.
        
        The scheduler will run daily at the configured time from SCHEDULER_SETTINGS.
        """
        try:
            hour = SCHEDULER_SETTINGS["daily_run_hour"]
            minute = SCHEDULER_SETTINGS["daily_run_minute"]
            
            # Add the daily job
            self.scheduler.add_job(
                func=self.run_daily_monitoring,
                trigger=CronTrigger(hour=hour, minute=minute),
                id='daily_job_monitoring',
                name='Daily Job Search Monitoring',
                replace_existing=True
            )
            
            self.logger.info(f"Scheduler started. Daily monitoring scheduled for {hour:02d}:{minute:02d}")
            self.logger.info("Press Ctrl+C to stop the scheduler")
            
            # Start the scheduler
            self.scheduler.start()
            
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {e}")
    
    def run_once(self):
        """Run job monitoring once (useful for testing)."""
        self.logger.info("Running job monitoring once...")
        self.run_daily_monitoring()
    
    def stop_scheduler(self):
        """Stop the scheduler gracefully."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("Scheduler stopped")


def main():
    """Main entry point for the scheduler."""
    # Get API key from configuration
    api_key = OPENAI_SETTINGS["api_key"]
    
    # Validate API key
    if not api_key or api_key == "your_openai_api_key_here":
        print("Error: OpenAI API key not configured.")
        print("Please set your API key in one of these ways:")
        print("   1. Create a .env file with OPENAI_API_KEY=your_key")
        print("   2. Set the OPENAI_API_KEY environment variable")
        print("   3. Get your API key from: https://platform.openai.com/api-keys")
        sys.exit(1)
    
    # Create scheduler
    scheduler = JobSearchScheduler(api_key)
    
    try:
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--run-once":
            # Run once for testing
            scheduler.run_once()
        else:
            # Start the scheduler for continuous monitoring
            scheduler.start_scheduler()
    
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop_scheduler()
    except Exception as e:
        print(f"Error: {e}")
        scheduler.stop_scheduler()


if __name__ == "__main__":
    main() 