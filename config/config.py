"""
Configuration file for Job Search Assistant.

This file contains all the filtering criteria and settings that can be easily modified
without changing the main script.
"""

import os
from pathlib import Path
from typing import List, Dict, Any

# Load environment variables
def load_env_file(env_path: str = "config/.env") -> Dict[str, str]:
    """Load environment variables from a .env file if it exists."""
    env_vars = {}
    env_file = Path(env_path)
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars

# Load environment variables
ENV_VARS = load_env_file()

# Job filtering criteria - customise these for your search preferences
FILTERING_CRITERIA = {
    # Acceptable locations for job opportunities
    "locations": [
        "Paris", "Remote", "France", "Europe", "Worldwide", 
        "Anywhere", "London", "Hybrid"
    ],
    
    # Keywords that should appear in job titles
    "title_keywords": [
        "data", "solutions architect", "AI", "machine learning", 
        "analytics", "engineer", "scientist", "analyst", "consultant"
    ],
    
    # Acceptable experience levels
    "experience_levels": [
        "intern", "junior", "entry-level", "associate", 
        "graduate", "new grad", "early career"
    ]
}

# File paths configuration
FILES = {
    "companies_csv": "config/companies_to_watch.csv",
    "results_markdown": "data/job_results.md",
    "database": ENV_VARS.get("DATABASE_PATH", "data/job_history.db")
}

# OpenAI API configuration
OPENAI_SETTINGS = {
    "model": "gpt-4o",
    "max_retries": 3,
    "api_key": ENV_VARS.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
}

# Scheduling configuration
SCHEDULER_SETTINGS = {
    "daily_run_hour": int(ENV_VARS.get("DAILY_RUN_HOUR", "9")),
    "daily_run_minute": int(ENV_VARS.get("DAILY_RUN_MINUTE", "0"))
}

# Dashboard configuration
DASHBOARD_SETTINGS = {
    "host": ENV_VARS.get("DASHBOARD_HOST", "localhost"),
    "port": int(ENV_VARS.get("DASHBOARD_PORT", "8501"))
}

# Output formatting
OUTPUT_SETTINGS = {
    "include_timestamp": True,
    "include_criteria_summary": True,
    "separator_style": "---"
} 