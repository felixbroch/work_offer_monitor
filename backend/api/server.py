#!/usr/bin/env python3
"""
Flask API Server for Job Search Assistant

This module provides REST API endpoints for the Next.js frontend,
enabling web-based interaction with the job monitoring system.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.database import JobDatabase, JobRecord
from src.core.history_tracker import JobHistoryTracker
from src.core.job_search_engine import JobSearchEngine
from src.core.scheduler import JobSearchScheduler
from config.config import FILES, OPENAI_SETTINGS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables for database connections
db = None
tracker = None


def initialize_database():
    """Initialize database connections."""
    global db, tracker
    try:
        db_path = FILES.get("database", "data/job_history.db")
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        db = JobDatabase(db_path)
        tracker = JobHistoryTracker(db)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key format."""
    return api_key and api_key.startswith('sk-') and len(api_key) > 20


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/validate-api-key', methods=['POST'])
def validate_api_key_endpoint():
    """Validate OpenAI API key."""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '')
        
        if not validate_api_key(api_key):
            return jsonify({
                'valid': False,
                'message': 'Invalid API key format. Must start with sk- and be at least 20 characters.'
            }), 400
        
        # Test the API key with a simple call
        try:
            engine = JobSearchEngine(api_key)
            # You could add a simple test call here if needed
            return jsonify({
                'valid': True,
                'message': 'API key format is valid'
            })
        except Exception as e:
            return jsonify({
                'valid': False,
                'message': f'API key validation failed: {str(e)}'
            }), 400
            
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs with optional filtering."""
    try:
        # Get query parameters
        status = request.args.get('status')
        company = request.args.get('company')
        limit = request.args.get('limit', type=int)
        search = request.args.get('search')
        
        # Get jobs from database
        jobs = db.get_all_jobs()
        
        # Convert to dictionaries
        job_list = []
        for job in jobs:
            job_dict = {
                'job_id': job.job_id,
                'company_name': job.company_name,
                'job_title': job.job_title,
                'location': job.location,
                'url': job.url,
                'description': job.description,
                'date_first_seen': job.date_first_seen.isoformat(),
                'date_last_seen': job.date_last_seen.isoformat(),
                'status': job.status,
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'updated_at': job.updated_at.isoformat() if job.updated_at else None
            }
            
            # Apply filters
            if status and job.status != status:
                continue
            if company and job.company_name.lower() != company.lower():
                continue
            if search and search.lower() not in (
                job.job_title.lower() + ' ' + 
                job.company_name.lower() + ' ' + 
                (job.location or '').lower()
            ):
                continue
                
            job_list.append(job_dict)
        
        # Apply limit
        if limit:
            job_list = job_list[:limit]
        
        return jsonify({
            'jobs': job_list,
            'total': len(job_list)
        })
        
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/jobs/statistics', methods=['GET'])
def get_job_statistics():
    """Get job statistics."""
    try:
        stats = db.get_job_statistics()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting job statistics: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/jobs/search', methods=['POST'])
def search_jobs():
    """Trigger job search for specific companies."""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        companies = data.get('companies', [])
        
        if not validate_api_key(api_key):
            return jsonify({
                'error': 'Invalid API key',
                'message': 'Please provide a valid OpenAI API key'
            }), 400
        
        if not companies:
            return jsonify({
                'error': 'No companies specified',
                'message': 'Please provide at least one company to search'
            }), 400
        
        # Initialize search engine with provided API key
        engine = JobSearchEngine(api_key)
        
        # Search for jobs
        all_jobs = []
        search_results = []
        
        for company_data in companies:
            try:
                company_name = company_data.get('company_name')
                career_url = company_data.get('career_page_url', '')
                
                if not company_name:
                    continue
                
                logger.info(f"Searching jobs for {company_name}")
                
                # Search for jobs
                search_result = engine.search_company_jobs(company_name, career_url)
                job_data_list = engine.extract_structured_jobs(search_result, company_name)
                
                # Process through history tracker
                summary = tracker.process_company_jobs(company_name, job_data_list)
                
                search_results.append({
                    'company_name': company_name,
                    'summary': summary,
                    'jobs_found': len(job_data_list)
                })
                
                all_jobs.extend(job_data_list)
                
            except Exception as e:
                logger.error(f"Error searching for {company_name}: {e}")
                search_results.append({
                    'company_name': company_name,
                    'error': str(e),
                    'jobs_found': 0
                })
        
        return jsonify({
            'success': True,
            'message': f'Search completed for {len(companies)} companies',
            'results': search_results,
            'total_jobs_found': len(all_jobs)
        })
        
    except Exception as e:
        logger.error(f"Error in job search: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get list of companies being monitored."""
    try:
        # Get unique companies from database
        companies = db.get_all_companies()
        return jsonify({
            'companies': companies
        })
        
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/companies', methods=['POST'])
def add_company():
    """Add a new company to monitor."""
    try:
        data = request.get_json()
        company_name = data.get('company_name')
        career_page_url = data.get('career_page_url', '')
        
        if not company_name:
            return jsonify({
                'error': 'Missing company name',
                'message': 'Company name is required'
            }), 400
        
        # Here you would typically save to your companies CSV or database
        # For now, just return success
        return jsonify({
            'success': True,
            'message': f'Company {company_name} added successfully'
        })
        
    except Exception as e:
        logger.error(f"Error adding company: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/jobs/export', methods=['GET'])
def export_jobs():
    """Export jobs to CSV format."""
    try:
        status_filter = request.args.get('status')
        company_filter = request.args.get('company')
        
        # Get jobs
        jobs = db.get_all_jobs()
        
        # Convert to CSV format
        csv_data = []
        headers = [
            'job_id', 'company_name', 'job_title', 'location', 'url', 
            'description', 'date_first_seen', 'date_last_seen', 'status'
        ]
        csv_data.append(','.join(headers))
        
        for job in jobs:
            # Apply filters
            if status_filter and job.status != status_filter:
                continue
            if company_filter and job.company_name.lower() != company_filter.lower():
                continue
            
            row = [
                job.job_id,
                job.company_name,
                job.job_title.replace(',', ';'),  # Escape commas
                job.location or '',
                job.url,
                (job.description or '').replace(',', ';')[:200],  # Truncate and escape
                job.date_first_seen.isoformat(),
                job.date_last_seen.isoformat(),
                job.status
            ]
            csv_data.append(','.join(f'"{field}"' for field in row))
        
        csv_content = '\n'.join(csv_data)
        
        return jsonify({
            'csv_data': csv_content,
            'filename': f'jobs_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        })
        
    except Exception as e:
        logger.error(f"Error exporting jobs: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    try:
        # Initialize database
        initialize_database()
        
        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))
        
        # Run the app
        app.run(
            host='0.0.0.0',
            port=port,
            debug=os.environ.get('FLASK_ENV') == 'development'
        )
        
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        sys.exit(1)
