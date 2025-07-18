#!/usr/bin/env python3
"""
Job Search Assistant - Dashboard

A Streamlit web interface for visualizing and exploring job search results.
Provides interactive charts, filtering, and detailed job information.
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import subprocess
import sys
from typing import Optional, List, Dict

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.database import JobDatabase, JobRecord
from src.core.history_tracker import JobHistoryTracker
from config.config import FILES


# Page configuration
st.set_page_config(
    page_title="Job Search Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border-left: 3px solid #6c757d;
        margin-bottom: 0.5rem;
    }
    .status-new {
        background-color: #e8f5e8;
        color: #2d5a2d;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .status-modified {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .status-seen {
        background-color: #e2e3e5;
        color: #383d41;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .status-removed {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_job_data():
    """Load job data from database."""
    try:
        db_path = FILES.get("database", "job_history.db")
        if not Path(db_path).exists():
            return pd.DataFrame(), {}
        
        db = JobDatabase(db_path)
        tracker = JobHistoryTracker(db)
        
        # Get all jobs
        jobs = db.get_all_jobs()
        
        # Convert to DataFrame
        if jobs:
            job_data = []
            for job in jobs:
                job_data.append({
                    'job_id': job.job_id,
                    'company_name': job.company_name,
                    'job_title': job.job_title,
                    'location': job.location,
                    'url': job.url,
                    'description': job.description,
                    'date_first_seen': job.date_first_seen,
                    'date_last_seen': job.date_last_seen,
                    'status': job.status
                })
            
            df = pd.DataFrame(job_data)
            df['date_first_seen'] = pd.to_datetime(df['date_first_seen'])
            df['date_last_seen'] = pd.to_datetime(df['date_last_seen'])
        else:
            df = pd.DataFrame()
        
        # Get statistics
        stats = tracker.get_status_summary()
        
        return df, stats
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), {}


def display_metrics(stats: Dict):
    """Display key metrics in a grid layout."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Jobs",
            value=stats.get('total_jobs', 0),
            delta=stats.get('new_jobs_today', 0),
            delta_color="normal"
        )
    
    with col2:
        new_jobs = stats.get('status_breakdown', {}).get('new', 0)
        st.metric(
            label="New Jobs",
            value=new_jobs,
            delta=None
        )
    
    with col3:
        modified_jobs = stats.get('status_breakdown', {}).get('modified', 0)
        st.metric(
            label="Modified Jobs",
            value=modified_jobs,
            delta=None
        )
    
    with col4:
        st.metric(
            label="Recent Activity",
            value=stats.get('recent_activity', 0),
            delta=None,
            help="Jobs updated in the last 7 days"
        )


def create_status_chart(df: pd.DataFrame):
    """Create a status distribution chart."""
    if df.empty:
        return None
    
    status_counts = df['status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Job Status Distribution",
        color_discrete_map={
            'new': '#28a745',
            'modified': '#ffc107',
            'seen': '#6c757d',
            'removed': '#dc3545'
        }
    )
    
    fig.update_layout(
        showlegend=True,
        height=400,
        title_x=0.5
    )
    
    return fig


def create_company_chart(df: pd.DataFrame):
    """Create a company distribution chart."""
    if df.empty:
        return None
    
    company_counts = df['company_name'].value_counts().head(10)
    
    fig = px.bar(
        x=company_counts.values,
        y=company_counts.index,
        orientation='h',
        title="Top 10 Companies by Job Count",
        labels={'x': 'Number of Jobs', 'y': 'Company'}
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig


def create_timeline_chart(df: pd.DataFrame):
    """Create a timeline chart showing job discovery over time."""
    if df.empty:
        return None
    
    # Group by date and status
    df['date'] = df['date_first_seen'].dt.date
    timeline_data = df.groupby(['date', 'status']).size().reset_index(name='count')
    
    fig = px.bar(
        timeline_data,
        x='date',
        y='count',
        color='status',
        title="Job Discovery Timeline",
        labels={'count': 'Number of Jobs', 'date': 'Date'},
        color_discrete_map={
            'new': '#28a745',
            'modified': '#ffc107',
            'seen': '#6c757d',
            'removed': '#dc3545'
        }
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Number of Jobs"
    )
    
    return fig


def display_job_table(df: pd.DataFrame, filters: Dict):
    """Display the job table with filtering options."""
    if df.empty:
        st.info("No jobs found in the database.")
        return
    
    # Apply filters
    filtered_df = df.copy()
    
    if filters['company']:
        filtered_df = filtered_df[filtered_df['company_name'].isin(filters['company'])]
    
    if filters['status']:
        filtered_df = filtered_df[filtered_df['status'].isin(filters['status'])]
    
    if filters['search']:
        search_mask = (
            filtered_df['job_title'].str.contains(filters['search'], case=False, na=False) |
            filtered_df['company_name'].str.contains(filters['search'], case=False, na=False) |
            filtered_df['location'].str.contains(filters['search'], case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # Date range filter
    if filters['date_range']:
        start_date, end_date = filters['date_range']
        filtered_df = filtered_df[
            (filtered_df['date_first_seen'].dt.date >= start_date) &
            (filtered_df['date_first_seen'].dt.date <= end_date)
        ]
    
    # Display results count
    st.subheader(f"Jobs ({len(filtered_df)} of {len(df)} total)")
    
    # Sort options
    sort_options = {
        'Most Recent': 'date_last_seen',
        'Oldest First': 'date_first_seen',
        'Company': 'company_name',
        'Job Title': 'job_title'
    }
    
    sort_by = st.selectbox(
        "Sort by:",
        options=list(sort_options.keys()),
        index=0
    )
    
    sort_ascending = sort_by in ['Company', 'Job Title']
    filtered_df = filtered_df.sort_values(
        by=sort_options[sort_by],
        ascending=sort_ascending
    )
    
    # Display table
    for _, job in filtered_df.iterrows():
        with st.expander(f"**{job['job_title']}** at {job['company_name']} - {job['location']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Status:** {job['status']}")
                st.write(f"**First Seen:** {job['date_first_seen'].strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Last Seen:** {job['date_last_seen'].strftime('%Y-%m-%d %H:%M')}")
                if job['description']:
                    st.write(f"**Description:** {job['description'][:200]}...")
            
            with col2:
                if job['url']:
                    st.link_button("Apply Now", job['url'])


def main():
    """Main dashboard function."""
    st.markdown('<div class="main-header">Job Search Assistant</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Filters")
    
    # Load data
    df, stats = load_job_data()
    
    if df.empty:
        st.warning("No job data found. Please run the job search first.")
        st.info("Run `python job_watch_web_search.py` to collect job data.")
        return
    
    # Display metrics
    display_metrics(stats)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        status_chart = create_status_chart(df)
        if status_chart:
            st.plotly_chart(status_chart, use_container_width=True)
    
    with col2:
        company_chart = create_company_chart(df)
        if company_chart:
            st.plotly_chart(company_chart, use_container_width=True)
    
    # Timeline chart
    timeline_chart = create_timeline_chart(df)
    if timeline_chart:
        st.plotly_chart(timeline_chart, use_container_width=True)
    
    # Filters
    filters = {}
    
    # Company filter
    companies = sorted(df['company_name'].unique())
    filters['company'] = st.sidebar.multiselect(
        "Companies",
        options=companies,
        default=[]
    )
    
    # Status filter
    statuses = sorted(df['status'].unique())
    filters['status'] = st.sidebar.multiselect(
        "Status",
        options=statuses,
        default=[]
    )
    
    # Search filter
    filters['search'] = st.sidebar.text_input(
        "Search",
        placeholder="Search jobs, companies, locations..."
    )
    
    # Date range filter
    min_date = df['date_first_seen'].dt.date.min()
    max_date = df['date_first_seen'].dt.date.max()
    
    filters['date_range'] = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Refresh button
    if st.sidebar.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Export button
    if st.sidebar.button("Export to CSV"):
        csv = df.to_csv(index=False)
        st.sidebar.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"job_search_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Display job table
    st.divider()
    display_job_table(df, filters)


if __name__ == "__main__":
    main()
