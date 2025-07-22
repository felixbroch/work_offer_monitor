#!/usr/bin/env python3
"""
Database Module for Job Search Assistant

This module handles all database operations for job tracking including:
- Job storage and retrieval
- Status tracking and history
- Data analysis and reporting
- Professional data management for web application deployment
"""

import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JobRecord:
    """Data class representing a job record in the database."""
    job_id: str
    company_name: str
    job_title: str
    location: str
    url: str
    description: str
    date_first_seen: datetime
    date_last_seen: datetime
    status: str
    hash_value: str


class JobDatabase:
    """
    SQLite database manager for job tracking and history.
    
    This class handles all database operations including job storage,
    status tracking, and historical data management.
    """
    
    def __init__(self, db_path: str = "job_history.db"):
        """
        Initialize the database connection and create tables if needed.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables and indexes."""
        db_file = Path(self.db_path)
        is_new_db = not db_file.exists()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create main jobs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        job_id TEXT PRIMARY KEY,
                        company_name TEXT NOT NULL,
                        job_title TEXT NOT NULL,
                        location TEXT DEFAULT '',
                        url TEXT NOT NULL,
                        description TEXT DEFAULT '',
                        date_first_seen TIMESTAMP NOT NULL,
                        date_last_seen TIMESTAMP NOT NULL,
                        status TEXT NOT NULL,
                        hash_value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create job history table for tracking status changes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company_name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_date ON jobs(date_last_seen)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_job_id ON job_history(job_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_date ON job_history(change_date)")
                
                conn.commit()
                
                if is_new_db:
                    self.logger.info(f"Created new database at {self.db_path}")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def generate_job_id(self, job_title: str, url: str) -> str:
        """
        Generate a unique job ID based on title and URL.
        
        Args:
            job_title (str): The job title
            url (str): The job application URL
            
        Returns:
            str: A unique job identifier
        """
        content = f"{job_title.lower().strip()}:{url.lower().strip()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def generate_hash(self, job_data: Dict) -> str:
        """
        Generate a hash for job data to detect changes.
        
        Args:
            job_data (Dict): Job data dictionary
            
        Returns:
            str: SHA256 hash of key job fields
        """
        content = (
            f"{job_data.get('title', '')}:"
            f"{job_data.get('location', '')}:"
            f"{job_data.get('description', '')}"
        )
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_existing_jobs(self, company_name: str) -> Dict[str, JobRecord]:
        """
        Get all existing jobs for a specific company.
        
        Args:
            company_name (str): Name of the company
            
        Returns:
            Dict[str, JobRecord]: Dictionary mapping job_id to JobRecord
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT job_id, company_name, job_title, location, url, description,
                           date_first_seen, date_last_seen, status, hash_value
                    FROM jobs 
                    WHERE company_name = ?
                """, (company_name,))
                
                jobs = {}
                for row in cursor.fetchall():
                    job = JobRecord(
                        job_id=row[0],
                        company_name=row[1],
                        job_title=row[2],
                        location=row[3],
                        url=row[4],
                        description=row[5],
                        date_first_seen=datetime.fromisoformat(row[6]),
                        date_last_seen=datetime.fromisoformat(row[7]),
                        status=row[8],
                        hash_value=row[9]
                    )
                    jobs[job.job_id] = job
                
                return jobs
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting existing jobs for {company_name}: {e}")
            return {}
    
    def insert_job(self, job_data: Dict) -> str:
        """
        Insert a new job record into the database.
        
        Args:
            job_data (Dict): Job data dictionary
            
        Returns:
            str: The job ID of the inserted job
        """
        job_id = self.generate_job_id(job_data['title'], job_data['url'])
        hash_value = self.generate_hash(job_data)
        now = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO jobs (job_id, company_name, job_title, location, url, description,
                                    date_first_seen, date_last_seen, status, hash_value)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_id,
                    job_data['company_name'],
                    job_data['title'],
                    job_data.get('location', ''),
                    job_data['url'],
                    job_data.get('description', ''),
                    now.isoformat(),
                    now.isoformat(),
                    'new',
                    hash_value
                ))
                
                # Add to history
                cursor.execute("""
                    INSERT INTO job_history (job_id, status)
                    VALUES (?, ?)
                """, (job_id, 'new'))
                
                conn.commit()
                
                return job_id
                
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting job {job_id}: {e}")
            raise
    
    def update_job(self, job_id: str, job_data: Dict, status: str = 'seen'):
        """
        Update an existing job record.
        
        Args:
            job_id (str): The job ID to update
            job_data (Dict): Updated job data
            status (str): New status for the job
        """
        hash_value = self.generate_hash(job_data)
        now = datetime.now()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current status
                cursor.execute("SELECT status FROM jobs WHERE job_id = ?", (job_id,))
                result = cursor.fetchone()
                current_status = result[0] if result else None
                
                # Update job record
                cursor.execute("""
                    UPDATE jobs 
                    SET job_title = ?, location = ?, description = ?, 
                        date_last_seen = ?, status = ?, hash_value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE job_id = ?
                """, (
                    job_data['title'],
                    job_data.get('location', ''),
                    job_data.get('description', ''),
                    now.isoformat(),
                    status,
                    hash_value,
                    job_id
                ))
                
                # Add to history if status changed
                if current_status != status:
                    cursor.execute("""
                        INSERT INTO job_history (job_id, status)
                        VALUES (?, ?)
                    """, (job_id, status))
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Error updating job {job_id}: {e}")
            raise
    
    def mark_jobs_removed(self, company_name: str, current_job_ids: List[str]) -> int:
        """
        Mark jobs as removed if they're no longer present in the current search.
        
        Args:
            company_name (str): Name of the company
            current_job_ids (List[str]): List of job IDs currently found
            
        Returns:
            int: Number of jobs marked as removed
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all active job IDs for the company
                cursor.execute("""
                    SELECT job_id FROM jobs 
                    WHERE company_name = ? AND status != 'removed'
                """, (company_name,))
                
                existing_job_ids = {row[0] for row in cursor.fetchall()}
                removed_job_ids = existing_job_ids - set(current_job_ids)
                
                # Mark removed jobs
                for job_id in removed_job_ids:
                    cursor.execute("""
                        UPDATE jobs 
                        SET status = 'removed', updated_at = CURRENT_TIMESTAMP
                        WHERE job_id = ?
                    """, (job_id,))
                    
                    cursor.execute("""
                        INSERT INTO job_history (job_id, status)
                        VALUES (?, ?)
                    """, (job_id, 'removed'))
                
                conn.commit()
                return len(removed_job_ids)
                
        except sqlite3.Error as e:
            self.logger.error(f"Error marking jobs as removed for {company_name}: {e}")
            return 0
    
    def get_job_statistics(self) -> Dict:
        """
        Get comprehensive statistics about job tracking.
        
        Returns:
            Dict: Dictionary containing various statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total jobs by status
                cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
                status_counts = dict(cursor.fetchall())
                
                # Jobs by company
                cursor.execute("SELECT company_name, COUNT(*) FROM jobs GROUP BY company_name")
                company_counts = dict(cursor.fetchall())
                
                # Recent activity (last 7 days)
                cursor.execute("""
                    SELECT COUNT(*) FROM jobs 
                    WHERE date_last_seen >= date('now', '-7 days')
                """)
                recent_activity = cursor.fetchone()[0]
                
                # New jobs in last 24 hours
                cursor.execute("""
                    SELECT COUNT(*) FROM jobs 
                    WHERE status = 'new' AND date_first_seen >= date('now', '-1 days')
                """)
                new_jobs_today = cursor.fetchone()[0]
                
                return {
                    'status_counts': status_counts,
                    'company_counts': company_counts,
                    'recent_activity': recent_activity,
                    'new_jobs_today': new_jobs_today,
                    'total_jobs': sum(status_counts.values())
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting job statistics: {e}")
            return {}
    
    def get_jobs_by_status(self, status: str, limit: int = 50) -> List[JobRecord]:
        """
        Get jobs filtered by status.
        
        Args:
            status (str): Status to filter by
            limit (int): Maximum number of jobs to return
            
        Returns:
            List[JobRecord]: List of matching job records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT job_id, company_name, job_title, location, url, description,
                           date_first_seen, date_last_seen, status, hash_value
                    FROM jobs 
                    WHERE status = ?
                    ORDER BY date_last_seen DESC
                    LIMIT ?
                """, (status, limit))
                
                jobs = []
                for row in cursor.fetchall():
                    job = JobRecord(
                        job_id=row[0],
                        company_name=row[1],
                        job_title=row[2],
                        location=row[3],
                        url=row[4],
                        description=row[5],
                        date_first_seen=datetime.fromisoformat(row[6]),
                        date_last_seen=datetime.fromisoformat(row[7]),
                        status=row[8],
                        hash_value=row[9]
                    )
                    jobs.append(job)
                
                return jobs
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting jobs by status {status}: {e}")
            return []
    
    def cleanup_old_records(self, days: int = 90) -> int:
        """
        Clean up old removed job records to keep database size manageable.
        
        Args:
            days (int): Number of days to keep removed jobs
            
        Returns:
            int: Number of records deleted
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM jobs 
                    WHERE status = 'removed' 
                    AND date_last_seen < date('now', '-{} days')
                """.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                self.logger.info(f"Cleaned up {deleted_count} old job records")
                return deleted_count
                
        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning up old records: {e}")
            return 0
    
    def get_all_jobs(self, company_filter: Optional[str] = None, 
                     status_filter: Optional[str] = None) -> List[JobRecord]:
        """
        Get all jobs with optional filtering.
        
        Args:
            company_filter (Optional[str]): Filter by company name
            status_filter (Optional[str]): Filter by status
            
        Returns:
            List[JobRecord]: List of matching job records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT job_id, company_name, job_title, location, url, description,
                           date_first_seen, date_last_seen, status, hash_value
                    FROM jobs 
                    WHERE 1=1
                """
                params = []
                
                if company_filter:
                    query += " AND company_name = ?"
                    params.append(company_filter)
                
                if status_filter:
                    query += " AND status = ?"
                    params.append(status_filter)
                
                query += " ORDER BY date_last_seen DESC"
                
                cursor.execute(query, params)
                
                jobs = []
                for row in cursor.fetchall():
                    job = JobRecord(
                        job_id=row[0],
                        company_name=row[1],
                        job_title=row[2],
                        location=row[3],
                        url=row[4],
                        description=row[5],
                        date_first_seen=datetime.fromisoformat(row[6]),
                        date_last_seen=datetime.fromisoformat(row[7]),
                        status=row[8],
                        hash_value=row[9]
                    )
                    jobs.append(job)
                
                return jobs
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting all jobs: {e}")
            return []
    
    def get_all_companies(self) -> List[str]:
        """
        Get list of all unique companies in the database.
        
        Returns:
            List[str]: List of unique company names
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT company_name 
                    FROM jobs 
                    ORDER BY company_name
                """)
                
                companies = [row[0] for row in cursor.fetchall()]
                return companies
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting companies: {e}")
            return [] 