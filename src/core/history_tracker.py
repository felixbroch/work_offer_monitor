#!/usr/bin/env python3
"""
Job History Tracker Module

This module handles job change detection, status management, and reporting
for the Job Search Assistant. It tracks job evolution over time and provides
detailed analytics on job market trends.
"""

import logging
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

from .database import JobDatabase, JobRecord


class JobHistoryTracker:
    """
    Tracks job history and manages status changes over time.
    
    This class is responsible for:
    - Detecting new, modified, and removed jobs
    - Managing job status transitions
    - Generating comprehensive reports
    - Handling data cleanup and exports
    """
    
    def __init__(self, db: JobDatabase):
        """
        Initialize the job history tracker.
        
        Args:
            db (JobDatabase): Database instance for job storage
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def process_company_jobs(self, company_name: str, current_jobs: List[Dict]) -> Dict:
        """
        Process jobs for a company and track changes.
        
        This method compares current job listings with stored data to detect:
        - New jobs (first time seen)
        - Modified jobs (content changed)
        - Unchanged jobs (same as before)
        - Removed jobs (no longer listed)
        
        Args:
            company_name (str): Name of the company
            current_jobs (List[Dict]): List of current job data
            
        Returns:
            Dict: Summary of processing results
        """
        self.logger.info(f"Processing {len(current_jobs)} jobs for {company_name}")
        
        # Get existing jobs from database
        existing_jobs = self.db.get_existing_jobs(company_name)
        
        # Initialize tracking lists
        new_jobs = []
        updated_jobs = []
        unchanged_jobs = []
        current_job_ids = []
        
        # Process each current job
        for job_data in current_jobs:
            # Ensure company name is included
            job_data['company_name'] = company_name
            
            # Generate job ID for tracking
            job_id = self.db.generate_job_id(job_data['title'], job_data['url'])
            current_job_ids.append(job_id)
            
            # Check if job already exists
            if job_id in existing_jobs:
                existing_job = existing_jobs[job_id]
                
                # Check if job content has changed
                new_hash = self.db.generate_hash(job_data)
                if new_hash != existing_job.hash_value:
                    # Job has been modified
                    self.db.update_job(job_id, job_data, 'modified')
                    updated_jobs.append(job_data)
                    self.logger.info(f"Job modified: {job_data['title']}")
                else:
                    # Job unchanged, update last seen timestamp
                    self.db.update_job(job_id, job_data, 'seen')
                    unchanged_jobs.append(job_data)
            else:
                # New job discovered
                self.db.insert_job(job_data)
                new_jobs.append(job_data)
                self.logger.info(f"New job found: {job_data['title']}")
        
        # Mark jobs as removed if they're no longer present
        removed_count = self.db.mark_jobs_removed(company_name, current_job_ids)
        
        if removed_count > 0:
            self.logger.info(f"Marked {removed_count} jobs as removed for {company_name}")
        
        # Return processing summary
        return {
            'company_name': company_name,
            'new_jobs': len(new_jobs),
            'updated_jobs': len(updated_jobs),
            'unchanged_jobs': len(unchanged_jobs),
            'removed_jobs': removed_count,
            'total_processed': len(current_jobs)
        }
    
    def get_status_summary(self) -> Dict:
        """
        Get a comprehensive summary of job statuses across all companies.
        
        Returns:
            Dict: Summary containing totals, breakdowns, and recent activity
        """
        stats = self.db.get_job_statistics()
        
        summary = {
            'total_jobs': stats['total_jobs'],
            'status_breakdown': stats['status_counts'],
            'company_breakdown': stats['company_counts'],
            'recent_activity': stats['recent_activity'],
            'new_jobs_today': stats.get('new_jobs_today', 0),
            'summary_date': datetime.now().isoformat()
        }
        
        return summary
    
    def get_new_jobs(self, limit: int = 20) -> List[JobRecord]:
        """
        Get recently added jobs.
        
        Args:
            limit (int): Maximum number of jobs to return
            
        Returns:
            List[JobRecord]: List of new job records
        """
        return self.db.get_jobs_by_status('new', limit)
    
    def get_modified_jobs(self, limit: int = 20) -> List[JobRecord]:
        """
        Get recently modified jobs.
        
        Args:
            limit (int): Maximum number of jobs to return
            
        Returns:
            List[JobRecord]: List of modified job records
        """
        return self.db.get_jobs_by_status('modified', limit)
    
    def get_removed_jobs(self, limit: int = 20) -> List[JobRecord]:
        """
        Get recently removed jobs.
        
        Args:
            limit (int): Maximum number of jobs to return
            
        Returns:
            List[JobRecord]: List of removed job records
        """
        return self.db.get_jobs_by_status('removed', limit)
    
    def generate_status_report(self) -> str:
        """
        Generate a comprehensive human-readable status report.
        
        Returns:
            str: Formatted markdown report
        """
        summary = self.get_status_summary()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""# Job Search Assistant - Status Report

**Generated:** {timestamp}

## Overview
- **Total Jobs Tracked:** {summary['total_jobs']}
- **Recent Activity** (last 7 days): {summary['recent_activity']} jobs
- **New Jobs Today:** {summary.get('new_jobs_today', 0)}

## Status Breakdown
"""
        
        # Status breakdown with better formatting
        status_order = ['new', 'seen', 'modified', 'removed']
        for status in status_order:
            count = summary['status_breakdown'].get(status, 0)
            if count > 0:
                report += f"- **{status.title()}:** {count}\n"
        
        # Add any other statuses not in the standard order
        for status, count in summary['status_breakdown'].items():
            if status not in status_order and count > 0:
                report += f"- **{status.title()}:** {count}\n"
        
        report += "\n## Company Breakdown\n"
        for company, count in sorted(summary['company_breakdown'].items()):
            report += f"- **{company}:** {count} jobs\n"
        
        # Add recent new jobs
        new_jobs = self.get_new_jobs(5)
        if new_jobs:
            report += "\n## Recent New Jobs\n"
            for job in new_jobs:
                report += f"### {job.job_title}\n"
                report += f"- **Company:** {job.company_name}\n"
                report += f"- **Location:** {job.location}\n"
                report += f"- **First Seen:** {job.date_first_seen.strftime('%Y-%m-%d %H:%M')}\n"
                report += f"- **Apply:** {job.url}\n\n"
        
        # Add recent modified jobs
        modified_jobs = self.get_modified_jobs(5)
        if modified_jobs:
            report += "\n## Recent Modified Jobs\n"
            for job in modified_jobs:
                report += f"### {job.job_title}\n"
                report += f"- **Company:** {job.company_name}\n"
                report += f"- **Location:** {job.location}\n"
                report += f"- **Last Updated:** {job.date_last_seen.strftime('%Y-%m-%d %H:%M')}\n"
                report += f"- **Apply:** {job.url}\n\n"
        
        report += "\n---\n"
        report += f"*Report generated by Job Search Assistant on {timestamp}*\n"
        
        return report
    
    def cleanup_old_data(self, days: int = 90) -> int:
        """
        Clean up old removed job records to maintain database performance.
        
        Args:
            days (int): Number of days to keep removed jobs before deletion
            
        Returns:
            int: Number of records cleaned up
        """
        deleted_count = self.db.cleanup_old_records(days)
        self.logger.info(f"Cleaned up {deleted_count} old job records (older than {days} days)")
        return deleted_count
    
    def export_jobs_to_csv(self, filename: str, status_filter: Optional[str] = None,
                          company_filter: Optional[str] = None):
        """
        Export jobs to CSV file for external analysis.
        
        Args:
            filename (str): Output CSV filename
            status_filter (Optional[str]): Filter by specific status
            company_filter (Optional[str]): Filter by specific company
        """
        try:
            # Get jobs based on filters
            jobs = self.db.get_all_jobs(company_filter, status_filter)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'job_id', 'company_name', 'job_title', 'location', 'url', 
                    'description', 'date_first_seen', 'date_last_seen', 'status'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for job in jobs:
                    writer.writerow({
                        'job_id': job.job_id,
                        'company_name': job.company_name,
                        'job_title': job.job_title,
                        'location': job.location,
                        'url': job.url,
                        'description': job.description,
                        'date_first_seen': job.date_first_seen.isoformat(),
                        'date_last_seen': job.date_last_seen.isoformat(),
                        'status': job.status
                    })
            
            self.logger.info(f"Exported {len(jobs)} jobs to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error exporting jobs to CSV: {e}")
            raise
    
    def get_job_trends(self, days: int = 30) -> Dict:
        """
        Analyze job trends over the specified period.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            Dict: Trend analysis data
        """
        # This would require more complex database queries
        # For now, return basic statistics
        stats = self.db.get_job_statistics()
        
        trends = {
            'period_days': days,
            'total_jobs': stats['total_jobs'],
            'recent_activity': stats['recent_activity'],
            'new_jobs_today': stats.get('new_jobs_today', 0),
            'analysis_date': datetime.now().isoformat()
        }
        
        return trends
    
    def get_company_performance(self, company_name: str) -> Dict:
        """
        Get performance metrics for a specific company.
        
        Args:
            company_name (str): Name of the company
            
        Returns:
            Dict: Company-specific metrics
        """
        # Get all jobs for the company
        jobs = self.db.get_all_jobs(company_filter=company_name)
        
        if not jobs:
            return {
                'company_name': company_name,
                'total_jobs': 0,
                'active_jobs': 0,
                'removed_jobs': 0,
                'last_activity': None
            }
        
        # Calculate metrics
        total_jobs = len(jobs)
        active_jobs = len([j for j in jobs if j.status in ['new', 'seen', 'modified']])
        removed_jobs = len([j for j in jobs if j.status == 'removed'])
        
        # Get last activity date
        last_activity = max(jobs, key=lambda x: x.date_last_seen).date_last_seen
        
        return {
            'company_name': company_name,
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'removed_jobs': removed_jobs,
            'last_activity': last_activity.isoformat()
        } 