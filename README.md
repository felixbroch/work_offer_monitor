# Job Search Assistant

A comprehensive automation tool designed to streamline the job search process. This personal project combines web scraping, intelligent filtering, and automated tracking to help identify and monitor relevant job opportunities.

## Project Purpose

The Job Search Assistant addresses the challenges of modern job hunting by automating key aspects of the search process:

- **Automated Discovery**: Uses OpenAI's web search API to find current job postings across target companies
- **Intelligent Filtering**: Matches opportunities based on location, keywords, and experience level preferences
- **Progress Tracking**: Maintains a complete history of job postings, tracking status changes over time
- **Trend Analysis**: Provides insights into hiring patterns and market trends
- **Application Support**: Generates structured data to support personalised applications

## Core Features

### Job Discovery
- **Web Search Integration**: Leverages OpenAI's web search capabilities for real-time job discovery
- **Multi-Company Monitoring**: Tracks opportunities across multiple target companies simultaneously
- **Smart Filtering**: Applies customisable criteria for location, job titles, and experience levels
- **Source Attribution**: Provides citations and direct links to original job postings

### Tracking & Analytics
- **Status Management**: Tracks jobs as new, modified, seen, or removed
- **Change Detection**: Automatically identifies when job postings are updated or removed
- **Historical Data**: Maintains complete job history with timestamps and status changes
- **Trend Analysis**: Provides insights into hiring patterns and company activity

### Dashboard & Reporting
- **Interactive Dashboard**: Streamlit-based web interface for data exploration
- **Visual Analytics**: Charts and graphs showing job trends and company breakdowns
- **Advanced Filtering**: Search and filter capabilities for detailed job analysis
- **Export Functionality**: CSV export for external analysis and application tracking

### Automation
- **Scheduled Monitoring**: Daily automated job searches with configurable timing
- **Report Generation**: Automatic daily status reports with key metrics
- **Data Management**: Automatic cleanup of old records to maintain performance

## Project Structure

```
job-search-assistant/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── job_search_engine.py    # Main job search engine
│   │   ├── database.py             # Database operations
│   │   ├── history_tracker.py      # Job history tracking
│   │   └── scheduler.py            # Task scheduling
│   └── dashboard/
│       ├── __init__.py
│       └── dashboard.py            # Streamlit dashboard
├── config/
│   ├── __init__.py
│   ├── config.py                   # Configuration settings
│   ├── .env.template               # Environment template
│   └── .env                        # Your environment variables
├── data/
│   ├── companies_to_watch.csv      # Companies to monitor
│   ├── job_results.db              # SQLite database
│   └── notifications_log.csv       # Notification history
├── logs/
│   └── job_monitor.log             # Application logs
├── scripts/
│   └── setup.py                    # Setup script
├── docs/
│   ├── JOB_TRACKING_DOCUMENTATION.md
│   └── DASHBOARD_README.md
├── main.py                         # Main CLI interface
├── run_dashboard.py                # Dashboard launcher
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

## Technologies Used

- **Python 3.10+**: Core development language
- **OpenAI API**: Web search and content analysis
- **SQLite**: Local database for job storage and history
- **Streamlit**: Interactive web dashboard
- **Plotly**: Data visualisation and charts
- **APScheduler**: Task scheduling and automation
- **Pandas**: Data manipulation and analysis
- **BeautifulSoup**: Web scraping (where applicable)

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- OpenAI API key with web search access
- Internet connection for API calls

### Installation

1. **Clone or download the repository**
   ```bash
   git clone https://github.com/FelixBROCHIER/job-search-assistant.git
   cd job-search-assistant
   ```

2. **Run the setup script**
   ```bash
   python scripts/setup.py
   ```
   
   This will:
   - Check Python version compatibility
   - Install required dependencies
   - Set up environment configuration
   - Create necessary directories
   - Configure default companies to monitor

3. **Configure API credentials**
   
   The setup script will prompt you for your OpenAI API key, or you can manually edit `config/.env`:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```
   
   Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

4. **Configure target companies**
   
   Edit `data/companies_to_watch.csv` to include your target companies:
   ```csv
   company_name,career_page_url
   ```

5. **Customise search criteria**
   
   Edit `config/config.py` to match your preferences:
   ```python
   FILTERING_CRITERIA = {
       "locations": ["London", "Remote", "Paris", "Europe"],
       "title_keywords": ["data scientist", "AI engineer", "analyst"],
       "experience_levels": ["graduate", "junior", "entry-level"]
   }
   ```

## Usage

### Manual Job Search
Run a one-time job search:
```bash
python main.py
```

### Automated Monitoring
Start daily automated monitoring:
```bash
# Start continuous scheduler (runs daily at 9 AM)
python main.py

# Run once for testing
python main.py --run-once
```

### Dashboard
Launch the interactive dashboard:
```bash
# Using the launcher script
python run_dashboard.py

# Or directly with Streamlit
streamlit run src/dashboard/dashboard.py
```

The dashboard provides:
- Interactive job listings with filtering
- Visual analytics and trend charts
- Company performance metrics
- CSV export functionality

## File Locations

After setup, your files will be organized as follows:

### Data Files
- `data/companies_to_watch.csv` - Target companies list
- `data/job_results.db` - SQLite database with job history
- `data/notifications_log.csv` - Notification history

### Configuration
- `config/config.py` - Application settings
- `config/.env` - Your API keys and environment variables

### Logs and Reports
- `logs/job_monitor.log` - Application execution logs
- `logs/job_results.md` - Latest search results
- `logs/daily_report_*.md` - Daily status reports

## How It Works

### Search Process
1. **Company Loading**: Reads target companies from CSV file
2. **Query Generation**: Creates search queries based on filtering criteria
3. **Web Search**: Uses OpenAI API to find current job postings
4. **Content Extraction**: Parses job titles, locations, requirements, and URLs
5. **Result Formatting**: Structures data for storage and analysis

### Tracking Process
1. **Job Discovery**: New jobs are marked as "new"
2. **Change Detection**: Modified jobs are marked as "modified"
3. **Status Updates**: Existing jobs are marked as "seen"
4. **Removal Tracking**: Missing jobs are marked as "removed"
5. **History Logging**: All changes are recorded with timestamps

### Dashboard Features
1. **Data Loading**: Connects to SQLite database for real-time data
2. **Interactive Filters**: Filter by company, status, location, and date range
3. **Visual Analytics**: Charts showing trends and distributions
4. **Job Details**: Expandable job listings with full information
5. **Export Options**: CSV download for external analysis

## Customisation

### Adapting for Different Roles
- Modify `FILTERING_CRITERIA` in `config.py` for your target roles
- Update company list in `companies_to_watch.csv`
- Adjust search queries in `job_watch_web_search.py` if needed

### Adding New Features
- **Email Notifications**: Add SMTP configuration for job alerts
- **Advanced Filtering**: Extend criteria for salary, company size, etc.
- **Application Tracking**: Add fields for application status
- **Integration**: Connect with LinkedIn, job boards, or ATS systems

### Performance Tuning
- Adjust `max_retries` in `config.py` for API reliability
- Modify cleanup schedules in `scheduler.py`
- Configure database indexes for large datasets

## Notes and Considerations

### API Usage
- Requires OpenAI API key with web search capabilities
- API calls are rate-limited and may incur costs
- Respectful delays between requests to avoid overwhelming servers

### Data Privacy
- All data is stored locally in SQLite database
- No personal information is transmitted to external services
- API keys are stored locally in environment variables

### Limitations
- Depends on OpenAI API availability and accuracy
- Search results may vary based on API performance
- Some job postings may not be detected due to site structure

## Future Enhancements

- **Mobile App**: React Native or Flutter interface
- **Machine Learning**: Job relevance scoring and recommendations
- **Integration**: Connect with popular job boards and ATS systems
- **Collaboration**: Multi-user support for team job searches
- **Analytics**: Advanced market analysis and salary insights