# Job Tracking System Documentation

## Overview

The job tracking system automatically monitors job postings across multiple companies, tracks their evolution over time, and maintains a comprehensive history in a SQLite database.

## Architecture

### Core Components

1. **`database.py`** - SQLite database management
2. **`history_tracker.py`** - Job change detection and status management
3. **`scheduler.py`** - Automated daily monitoring using APScheduler
4. **`job_watch_web_search.py`** - OpenAI web search integration

## Database Schema

### Jobs Table
```sql
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,           -- Unique identifier (MD5 hash of title + URL)
    company_name TEXT NOT NULL,        -- Company name
    job_title TEXT NOT NULL,           -- Job title
    location TEXT,                     -- Job location
    url TEXT NOT NULL,                 -- Application URL
    description TEXT,                  -- Job description
    date_first_seen TIMESTAMP NOT NULL, -- When job was first discovered
    date_last_seen TIMESTAMP NOT NULL,  -- When job was last seen
    status TEXT NOT NULL,              -- Current status: new/seen/modified/removed
    hash_value TEXT NOT NULL,          -- SHA256 hash of job content for change detection
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Job History Table
```sql
CREATE TABLE job_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,              -- Reference to jobs table
    status TEXT NOT NULL,              -- Status at this point in time
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
);
```

## Job Status Lifecycle

### Status Types

1. **`new`** - Job discovered for the first time
2. **`seen`** - Job still present, unchanged since last check
3. **`modified`** - Job content has changed (title, location, description)
4. **`removed`** - Job no longer available

### Status Transitions

```
[Job Found] → new
    ↓
[Still Present] → seen
    ↓
[Content Changed] → modified
    ↓
[No Longer Found] → removed
```

## 🧠 Change Detection Logic

### Job ID Generation
```python
def generate_job_id(self, job_title: str, url: str) -> str:
    content = f"{job_title.lower().strip()}:{url.lower().strip()}"
    return hashlib.md5(content.encode()).hexdigest()
```

### Content Hash Generation
```python
def generate_hash(self, job_data: Dict) -> str:
    content = f"{job_data.get('title', '')}:{job_data.get('location', '')}:{job_data.get('description', '')}"
    return hashlib.sha256(content.encode()).hexdigest()
```

### Change Detection Process

1. **New Job Detection**: Job ID not found in database → status = "new"
2. **Content Change Detection**: Hash value differs from stored hash → status = "modified"
3. **Removal Detection**: Job ID not in current results → status = "removed"
4. **No Change**: Hash value matches → status = "seen"

## ⏰ Scheduling System

### Daily Monitoring
- **Schedule**: Every day at 9:00 AM
- **Trigger**: CronTrigger(hour=9, minute=0)
- **Process**: 
  1. Load companies from CSV
  2. Search each company using OpenAI web search
  3. Extract job data from search results
  4. Process through history tracker
  5. Generate daily report
  6. Cleanup old data (weekly on Mondays)

### Usage

```bash
# Start the scheduler (runs daily at 9 AM)
python scheduler.py

# Run once for testing
python scheduler.py --run-once
```

## Status Tracking Process

### Step-by-Step Workflow

1. **Load Existing Jobs**
   ```python
   existing_jobs = db.get_existing_jobs(company_name)
   ```

2. **Process Current Jobs**
   ```python
   for job_data in current_jobs:
       job_id = db.generate_job_id(job_data['title'], job_data['url'])
       
       if job_id in existing_jobs:
           # Check for changes
           new_hash = db.generate_hash(job_data)
           if new_hash != existing_jobs[job_id].hash_value:
               db.update_job(job_id, job_data, 'modified')
           else:
               db.update_job(job_id, job_data, 'seen')
       else:
           # New job
           db.insert_job(job_data)
   ```

3. **Mark Removed Jobs**
   ```python
   removed_count = db.mark_jobs_removed(company_name, current_job_ids)
   ```

## Reporting and Analytics

### Daily Reports
- Generated automatically after each monitoring run
- Saved as `daily_report_YYYY-MM-DD.md`
- Includes:
  - Total jobs tracked
  - Status breakdown
  - Company breakdown
  - Recent new/modified jobs

### Statistics Available
```python
stats = db.get_job_statistics()
# Returns:
{
    'status_counts': {'new': 5, 'seen': 45, 'modified': 2, 'removed': 3},
    'company_counts': {'Google': 15, 'Microsoft': 12, 'OpenAI': 8},
    'recent_activity': 25,  # Jobs seen in last 7 days
    'total_jobs': 55
}
```

## 🧹 Data Management

### Automatic Cleanup
- **Frequency**: Weekly (Mondays)
- **Action**: Removes jobs marked as "removed" older than 90 days
- **Purpose**: Keep database size manageable

### Manual Cleanup
```python
deleted_count = tracker.cleanup_old_data(days=90)
```

## Configuration

### Database Settings
- **Database File**: `job_history.db` (configurable)
- **Backup**: Consider regular backups of the SQLite file
- **Location**: Same directory as scripts

### Logging
- **Log File**: `job_monitor.log`
- **Level**: INFO
- **Format**: Timestamp, module, level, message

## Usage Examples

### Basic Monitoring
```python
from database import JobDatabase
from history_tracker import JobHistoryTracker

# Initialize
db = JobDatabase("job_history.db")
tracker = JobHistoryTracker(db)

# Process jobs for a company
summary = tracker.process_company_jobs("Google", job_data_list)
print(f"New: {summary['new_jobs']}, Modified: {summary['updated_jobs']}")
```

### Get Recent Jobs
```python
# Get new jobs
new_jobs = tracker.get_new_jobs(limit=10)

# Get modified jobs
modified_jobs = tracker.get_modified_jobs(limit=10)

# Get removed jobs
removed_jobs = tracker.get_removed_jobs(limit=10)
```

### Export Data
```python
# Export new jobs to CSV
tracker.export_jobs_to_csv("new_jobs.csv", status_filter="new")
```

## Monitoring and Debugging

### Log Files
- **`job_monitor.log`**: Detailed execution logs
- **`daily_report_*.md`**: Daily status reports

### Database Queries
```sql
-- View all jobs for a company
SELECT * FROM jobs WHERE company_name = 'Google';

-- View recent changes
SELECT * FROM job_history ORDER BY change_date DESC LIMIT 10;

-- View status distribution
SELECT status, COUNT(*) FROM jobs GROUP BY status;
```

## Troubleshooting

### Common Issues

1. **No jobs being tracked**
   - Check OpenAI API key
   - Verify company URLs are accessible
   - Check log files for errors

2. **Database errors**
   - Ensure write permissions in directory
   - Check SQLite file integrity
   - Verify database schema

3. **Scheduler not running**
   - Check if APScheduler is installed
   - Verify system time is correct
   - Check for conflicting processes

### Performance Considerations

- **Database Indexes**: Automatically created for common queries
- **Hash Comparison**: Efficient change detection using SHA256
- **Batch Processing**: Process companies sequentially to avoid rate limits
- **Cleanup**: Regular cleanup prevents database bloat

## 🔮 Future Enhancements

- Email notifications for new jobs
- Web dashboard for job tracking
- Advanced filtering and search
- Integration with job application tracking
- Machine learning for job relevance scoring
- API endpoints for external access 