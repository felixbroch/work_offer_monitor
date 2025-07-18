# Job Watch Dashboard

A beautiful and interactive Streamlit web application to visualize and explore job monitoring results from the Job Watch tool.

## Features

### **Interactive Dashboard**
- **Real-time metrics**: Total jobs, new jobs, companies, recent activity
- **Interactive charts**: Pie charts, bar charts, timeline graphs
- **Responsive design**: Works on desktop and mobile devices

### **Advanced Filtering**
- **Company filter**: Multi-select dropdown for companies
- **Status filter**: Filter by new, seen, modified, removed jobs
- **Location filter**: Search by job location
- **Date range**: Filter by when jobs were last seen
- **Text search**: Search job titles with real-time filtering

### **Job Listings Table**
- **Clickable URLs**: Direct links to job applications
- **Status badges**: Color-coded status indicators
- **Company badges**: Visual company identification
- **Sortable columns**: Click headers to sort
- **Export functionality**: Download filtered results as CSV

### **Live Data Integration**
- **Database connection**: Direct SQLite database integration
- **Refresh button**: Run job monitoring from the dashboard
- **Auto-reload**: Automatic data refresh capabilities

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Ensure Job Data Exists
Make sure you have job data by running:
```bash
python scheduler.py --run-once
```

## Usage

### Method 1: Using the Launcher Script
```bash
python run_dashboard.py
```

### Method 2: Direct Streamlit Command
```bash
streamlit run app.py
```

### Method 3: Manual Launch
```bash
python -m streamlit run app.py
```

## Dashboard Sections

### 1. **Header Section**
- Main title with job watch icon
- Clean, professional styling

### 2. **Metrics Row**
- **Total Jobs**: Count of all jobs in database
- **New Jobs**: Recently discovered jobs (with delta indicator)
- **Companies**: Number of unique companies
- **Recent (7 days)**: Jobs seen in the last week

### 3. **Charts Section**
- **Jobs by Status**: Pie chart showing status distribution
- **Jobs by Company**: Horizontal bar chart of top companies
- **Job Activity Timeline**: Line chart showing job discovery over time

### 4. **Filters Sidebar**
- **Company**: Multi-select dropdown
- **Status**: Checkbox selection
- **Location**: Multi-select dropdown
- **Date Range**: Date picker for last seen dates
- **Search**: Text input for job title search

### 5. **Job Listings Table**
- **Company**: Company name with badge
- **Job Title**: Full job title
- **Location**: Job location
- **Status**: Color-coded status badge
- **First Seen**: When job was first discovered
- **Last Seen**: When job was last seen
- **URL**: Clickable application link

### 6. **Action Buttons**
- **Refresh Data**: Run job monitoring and reload data
- **Export to CSV**: Download filtered results

## Visual Design

### Color Scheme
- **New jobs**: Green (#28a745)
- **Seen jobs**: Blue (#17a2b8)
- **Modified jobs**: Yellow (#ffc107)
- **Removed jobs**: Red (#dc3545)
- **Company badges**: Gray (#e9ecef)

### Responsive Layout
- **Wide layout**: Optimized for desktop screens
- **Mobile-friendly**: Responsive design for mobile devices
- **Sidebar**: Collapsible filters panel

## Configuration

### Database Connection
The dashboard automatically connects to:
- **Primary**: `job_history.db` (SQLite database)
- **Fallback**: `job_results.csv` (CSV file)

### Customization
You can modify the dashboard by editing:
- **Styling**: CSS in the `st.markdown()` section
- **Charts**: Plotly configuration in chart sections
- **Filters**: Filter logic in the sidebar section

## Browser Compatibility

- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support
- **Mobile browsers**: Responsive design

## 🚨 Troubleshooting

### Common Issues

1. **"No job data found"**
   - Run job monitoring first: `python scheduler.py --run-once`
   - Check if `job_history.db` exists

2. **Dashboard won't start**
   - Ensure Streamlit is installed: `pip install streamlit`
   - Check if `app.py` exists in the current directory

3. **Charts not loading**
   - Ensure Plotly is installed: `pip install plotly`
   - Check browser console for JavaScript errors

4. **Database connection error**
   - Verify `job_history.db` file permissions
   - Check if database is corrupted

### Performance Tips

- **Large datasets**: Use filters to reduce data size
- **Slow loading**: Consider pagination for very large datasets
- **Memory usage**: Close unused browser tabs

## Data Refresh

### Automatic Refresh
- Data is loaded fresh each time the dashboard starts
- No automatic background refresh (manual refresh button)

### Manual Refresh
1. Click "Refresh Data" button
2. Wait for job monitoring to complete
3. Dashboard will reload automatically

## Data Export

### CSV Export
- Click "Export to CSV" button
- Downloads filtered results only
- Includes all job details
- Timestamped filename

### Export Format
```csv
job_id,company_name,job_title,location,url,description,date_first_seen,date_last_seen,status
```

## 🔮 Future Enhancements

- **Real-time updates**: WebSocket connection for live data
- **Email notifications**: Alert system for new jobs
- **Advanced analytics**: Machine learning insights
- **User authentication**: Multi-user support
- **API endpoints**: REST API for external access
- **Mobile app**: Native mobile application

## 📄 File Structure

```
job-watch/
├── app.py                    # Main Streamlit application
├── run_dashboard.py          # Dashboard launcher script
├── job_history.db           # SQLite database
├── scheduler.py             # Job monitoring scheduler
├── database.py              # Database management
├── history_tracker.py       # Job tracking logic
├── requirements.txt         # Python dependencies
└── DASHBOARD_README.md      # This file
```

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run job monitoring** (if no data exists):
   ```bash
   python scheduler.py --run-once
   ```

3. **Launch dashboard**:
   ```bash
   python run_dashboard.py
   ```

4. **Open browser**: Navigate to `http://localhost:8501`

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review the main project README
- Check the job monitoring logs

---

**Job Watch Dashboard** - Transform your job monitoring data into actionable insights! 