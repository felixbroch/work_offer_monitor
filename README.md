# Job Search Assistant

A comprehensive, AI-powered job monitoring and application tracking system built with Next.js and Python. This professional-grade application streamlines the job search process by automatically discovering relevant opportunities, tracking their evolution over time, and providing actionable insights through an intuitive web interface.

## Features

### Intelligent Job Discovery
- **AI-Powered Search**: Leverages OpenAI's advanced models to discover relevant job opportunities across multiple companies
- **Automated Monitoring**: Continuous tracking of job postings with intelligent change detection
- **Smart Filtering**: Configurable criteria for location, experience level, and job categories
- **Multi-Company Support**: Monitor dozens of companies simultaneously with targeted searches

### Professional Web Interface
- **Modern Dashboard**: Clean, responsive Next.js frontend with real-time analytics
- **Interactive Job Management**: Filter, search, and categorise opportunities with advanced controls
- **Visual Analytics**: Charts and metrics to understand job market trends and discovery patterns
- **Export Capabilities**: Download job data in CSV format for external analysis

### Advanced Tracking System
- **Status Management**: Automatic detection of new, modified, and removed job postings
- **Historical Data**: Comprehensive database of job evolution and market changes
- **Trend Analysis**: Insights into company hiring patterns and market dynamics
- **Notification System**: Stay informed about new opportunities and important changes

### Enterprise-Ready Architecture
- **Scalable Backend**: Python-based API with SQLite database for reliable data management
- **Containerised Deployment**: Ready for deployment on Vercel, AWS, or other cloud platforms
- **Security-First**: API key management and secure data handling practices
- **Performance Optimised**: Efficient database queries and responsive user interface

## Technologies Used

### Frontend
- **Next.js 14**: Modern React framework with App Router
- **TypeScript**: Type-safe development with excellent IDE support
- **Tailwind CSS**: Utility-first styling for consistent, responsive design
- **Recharts**: Professional charts and data visualisation
- **Lucide React**: High-quality icon system

### Backend
- **Python 3.9+**: Core development language
- **Flask**: Lightweight web framework for API endpoints
- **SQLite**: Embedded database for reliable data storage
- **OpenAI API**: Advanced AI capabilities for job discovery
- **APScheduler**: Task scheduling for automated monitoring

### Deployment & DevOps
- **Vercel**: Serverless deployment platform
- **Git**: Version control with professional branching strategy
- **Environment Management**: Secure configuration handling

## Project Structure

```
job-search-assistant/
├── app/                           # Next.js application
│   ├── globals.css               # Global styles and Tailwind configuration
│   ├── layout.tsx                # Root layout component
│   └── page.tsx                  # Main application page
├── components/                    # React components
│   ├── ApiKeyModal.tsx           # API key configuration modal
│   ├── Dashboard.tsx             # Analytics dashboard
│   ├── JobList.tsx               # Job listings with filtering
│   ├── JobSearch.tsx             # Job search interface
│   └── CompanyManager.tsx        # Company management interface
├── backend/                       # Python backend
│   └── api/
│       └── server.py             # Flask API server
├── src/                          # Python core modules
│   └── core/
│       ├── database.py           # Database management
│       ├── history_tracker.py    # Job change tracking
│       ├── job_search_engine.py  # AI-powered job discovery
│       └── scheduler.py          # Automated monitoring
├── config/
│   ├── config.py                 # Application configuration
│   └── companies_to_watch.csv    # Company monitoring list
├── data/                         # Data storage
├── docs/                         # Documentation
├── package.json                  # Node.js dependencies
├── requirements.txt              # Python dependencies
├── vercel.json                   # Deployment configuration
└── README.md                     # Project documentation
```

## Getting Started

### Prerequisites

- **Node.js 18+**: Required for Next.js frontend
- **Python 3.9+**: Required for backend services
- **OpenAI API Key**: Get yours from [OpenAI Platform](https://platform.openai.com/api-keys)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/job-search-assistant.git
   cd job-search-assistant
   ```

2. **Install dependencies**
   ```bash
   # Install Node.js dependencies
   npm install
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   # Add your OpenAI API key and other settings
   ```

4. **Start the development servers**
   ```bash
   # Terminal 1: Start the Python API server
   python backend/api/server.py
   
   # Terminal 2: Start the Next.js development server
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:5000

### Production Deployment on Vercel

1. **Prepare for deployment**
   ```bash
   # Ensure all dependencies are up to date
   npm install
   pip freeze > requirements.txt
   ```

2. **Deploy to Vercel**
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Deploy the application
   vercel --prod
   ```

3. **Configure environment variables**
   - Set `OPENAI_API_KEY` in your Vercel dashboard
   - Configure other environment variables as needed

## Usage Guide

### Initial Setup

1. **Access the application** at your deployed URL or localhost:3000
2. **Configure your OpenAI API key** when prompted
3. **Add companies** you're interested in monitoring
4. **Run your first job search** to discover opportunities

### Managing Job Searches

1. **Dashboard Tab**: View analytics, trends, and recent activity
2. **Jobs Tab**: Browse all discovered opportunities with advanced filtering
3. **Search Tab**: Trigger new job searches for specific companies
4. **Companies Tab**: Manage your list of companies to monitor

### Advanced Features

- **Automated Monitoring**: Set up daily job monitoring using the scheduler
- **Data Export**: Download job data for external analysis
- **Status Tracking**: Monitor job lifecycle from discovery to application
- **Trend Analysis**: Understand hiring patterns and market dynamics

## Configuration

### Job Search Criteria

Edit `config/config.py` to customise:

```python
FILTERING_CRITERIA = {
    "locations": ["London", "Remote", "Europe"],
    "title_keywords": ["engineer", "developer", "data scientist"],
    "experience_levels": ["junior", "senior", "lead"]
}
```

### Company Monitoring

Add companies to `data/companies_to_watch.csv`:

```csv
company_name,career_page_url
Google,https://careers.google.com/
Microsoft,https://careers.microsoft.com/
```

### Environment Variables

Key configuration options:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DATABASE_PATH`: Path to SQLite database file
- `DAILY_RUN_HOUR`: Hour for automated monitoring (0-23)
- `BACKEND_URL`: API server URL for production

## API Documentation

### Core Endpoints

- `GET /api/backend/jobs` - Retrieve job listings
- `POST /api/backend/jobs/search` - Trigger job search
- `GET /api/backend/jobs/statistics` - Get analytics data
- `GET /api/backend/companies` - List monitored companies
- `POST /api/backend/validate-api-key` - Validate OpenAI API key

### Response Formats

All API responses follow consistent JSON formats with proper error handling and status codes.

## Database Schema

### Jobs Table
- Comprehensive job information with unique identifiers
- Change tracking with timestamps and status management
- Content hashing for efficient change detection

### Job History Table
- Complete audit trail of job status changes
- Historical analysis capabilities
- Data retention policies for performance

## Performance & Scalability

### Database Optimisation
- Indexed queries for fast retrieval
- Automatic cleanup of old records
- Efficient change detection algorithms

### API Performance
- Asynchronous job processing
- Rate limiting for external API calls
- Caching strategies for frequently accessed data

### Frontend Optimisation
- Server-side rendering with Next.js
- Optimised bundle sizes
- Progressive loading and caching

## Troubleshooting

### Common Issues

**Application won't start**
- Verify Node.js and Python versions
- Check all dependencies are installed
- Ensure environment variables are configured

**API key validation fails**
- Verify your OpenAI API key is correct
- Check API key has sufficient credits
- Ensure no extra spaces or characters

**No jobs being discovered**
- Verify company names and URLs are correct
- Check OpenAI API connectivity
- Review search criteria in configuration

**Database errors**
- Ensure write permissions for data directory
- Check SQLite file isn't corrupted
- Verify database schema is up to date

### Debug Mode

Enable detailed logging:
```bash
export FLASK_ENV=development
export DEBUG=true
```

## Contributing

We welcome contributions to improve the Job Search Assistant. Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request with a clear description

### Development Standards

- Follow TypeScript and Python best practices
- Maintain test coverage for new features
- Use conventional commit messages
- Update documentation for significant changes

## Security Considerations

- **API Key Security**: Never commit API keys to version control
- **Data Privacy**: Job data is stored locally or in your chosen database
- **Secure Communication**: HTTPS enforced in production
- **Input Validation**: All user inputs are properly validated

## Limitations & Future Enhancements

### Current Limitations
- Requires manual API key configuration
- Limited to OpenAI-supported job search capabilities
- Single-user application (no multi-tenancy)

### Planned Enhancements
- **Email Notifications**: Automated alerts for new opportunities
- **Application Tracking**: Integration with job application management
- **Advanced Analytics**: Machine learning for job relevance scoring
- **Multi-User Support**: Team-based job monitoring
- **Integration APIs**: Connect with LinkedIn, Indeed, and other platforms

## Licence

This project is licensed under the MIT Licence. See the [LICENCE](LICENCE) file for details.

## Support

For support, please:

1. Check the troubleshooting section above
2. Review the documentation in the `docs/` directory
3. Open an issue on GitHub with detailed information about your problem

## Contributing

We welcome contributions to improve the Job Search Assistant. Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request with a clear description

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
├── config/
│   ├── __init__.py
│   ├── config.py                   # Configuration settings
│   ├── .env.template               # Environment template
│   └── .env                        # Your environment variables
├── data/
│   ├── companies_to_watch.csv      # Companies to monitor
│   ├── job_results.db              # SQLite database
│   └── notifications_log.csv       # Notification history
├── scripts/
│   └── setup.py                    # Setup script
├── docs/
│   ├── JOB_TRACKING_DOCUMENTATION.md
│   └── DEPLOYMENT.md
├── main.py                         # Main CLI interface
├── start_dev.py                    # Development server launcher
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

## Technologies Used

- **Python 3.10+**: Core development language  
- **OpenAI API**: Web search and content analysis
- **SQLite**: Local database for job storage and history
- **Flask**: API backend for web interface
- **Next.js**: Modern React framework for frontend
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **APScheduler**: Task scheduling and automation

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
# Start development servers
python start_dev.py

# Or start manually
npm run dev  # Frontend
python backend/api/server.py  # Backend
```

The web interface provides:
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