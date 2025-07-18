"""
Job Search Assistant - Core Package

This package contains the core functionality for the Job Search Assistant,
including job search engines, database management, and tracking systems.
"""

__version__ = "1.0.0"
__author__ = "Felix Brochier"
__email__ = "felix.brochier@example.com"

# Import main classes for easy access
from .core.database import JobDatabase, JobRecord
from .core.history_tracker import JobHistoryTracker
from .core.scheduler import JobSearchScheduler
from .core.job_search_engine import JobSearchEngine

__all__ = [
    'JobDatabase',
    'JobRecord', 
    'JobHistoryTracker',
    'JobSearchScheduler',
    'JobSearchEngine'
]
