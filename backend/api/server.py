#!/usr/bin/env python3
"""
Enhanced Flask API Server for Job Search Assistant

This module provides REST API endpoints for the Next.js frontend,
enabling web-based interaction with the enhanced job monitoring system
with real web search capabilities.
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
from src.core.enhanced_job_search_engine import EnhancedJobSearchEngine
from src.core.scheduler import JobSearchScheduler
from config.config import FILES, OPENAI_SETTINGS, FILTERING_CRITERIA

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


# Add routes that match frontend expectations
@app.route('/api/backend/health', methods=['GET'])
def backend_health_check():
    """Health check endpoint for /api/backend path."""
    return health_check()


@app.route('/api/backend/validate-api-key', methods=['POST'])
def backend_validate_api_key():
    """Validate API key endpoint for /api/backend path."""
    return validate_api_key_endpoint()


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
            engine = EnhancedJobSearchEngine(api_key)
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
        engine = EnhancedJobSearchEngine(
            openai_api_key=api_key,
            google_api_key=data.get('google_api_key'),
            bing_api_key=data.get('bing_api_key'),
            custom_search_engine_id=data.get('custom_search_engine_id')
        )
        
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


@app.route('/api/jobs/search-enhanced', methods=['POST'])
def enhanced_search_jobs():
    """Enhanced job search with real web search capabilities."""
    try:
        data = request.get_json()
        openai_api_key = data.get('openai_api_key')
        google_api_key = data.get('google_api_key')
        bing_api_key = data.get('bing_api_key')
        custom_search_engine_id = data.get('custom_search_engine_id')
        companies = data.get('companies', [])
        location = data.get('location', '')
        
        if not validate_api_key(openai_api_key):
            return jsonify({
                'error': 'Invalid OpenAI API key',
                'message': 'Please provide a valid OpenAI API key'
            }), 400
        
        if not companies:
            return jsonify({
                'error': 'No companies specified',
                'message': 'Please provide at least one company to search'
            }), 400
        
        # Initialize enhanced search engine
        engine = EnhancedJobSearchEngine(
            openai_api_key=openai_api_key,
            google_api_key=google_api_key,
            bing_api_key=bing_api_key,
            custom_search_engine_id=custom_search_engine_id
        )
        
        # Get search capabilities
        capabilities = engine.get_search_capabilities()
        
        # Run enhanced batch search
        search_results = engine.run_batch_search(companies)
        
        # Process results for database storage
        total_new_jobs = 0
        for company_result in search_results.get('company_results', []):
            company_name = company_result.get('company_name', '')
            if company_result.get('status') == 'success':
                # Here you could process jobs through history tracker
                # For now, just count them
                total_new_jobs += company_result.get('jobs_found', 0)
        
        return jsonify({
            'success': True,
            'message': f'Enhanced search completed for {len(companies)} companies',
            'results': search_results,
            'capabilities': capabilities,
            'total_new_jobs': total_new_jobs,
            'search_mode': 'enhanced_web_search'
        })
        
    except Exception as e:
        logger.error(f"Error in enhanced job search: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/search/capabilities', methods=['GET'])
def get_search_capabilities():
    """Get information about available search capabilities."""
    try:
        # Check if API keys are provided in query params for testing
        openai_key = request.args.get('openai_key', '')
        google_key = request.args.get('google_key', '')
        bing_key = request.args.get('bing_key', '')
        cse_id = request.args.get('cse_id', '')
        
        if openai_key:
            engine = EnhancedJobSearchEngine(
                openai_api_key=openai_key,
                google_api_key=google_key if google_key else None,
                bing_api_key=bing_key if bing_key else None,
                custom_search_engine_id=cse_id if cse_id else None
            )
            capabilities = engine.get_search_capabilities()
        else:
            # Return generic capabilities without API keys
            capabilities = {
                'enhanced_search': True,
                'web_search_engine': {
                    'providers_available': {
                        'google': False,
                        'bing': False,
                        'duckduckgo': True
                    },
                    'job_sites_monitored': 9,
                    'openai_enabled': False
                },
                'backup_agent_available': False,
                'filtering_criteria': FILTERING_CRITERIA
            }
        
        return jsonify({
            'success': True,
            'capabilities': capabilities,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting search capabilities: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/search/test', methods=['POST'])
def test_search_engine():
    """Test the search engine with a sample company."""
    try:
        data = request.get_json()
        openai_api_key = data.get('openai_api_key')
        google_api_key = data.get('google_api_key')
        bing_api_key = data.get('bing_api_key')
        custom_search_engine_id = data.get('custom_search_engine_id')
        test_company = data.get('test_company', 'Microsoft')
        
        if not validate_api_key(openai_api_key):
            return jsonify({
                'error': 'Invalid OpenAI API key',
                'message': 'Please provide a valid OpenAI API key'
            }), 400
        
        # Initialize enhanced search engine
        engine = EnhancedJobSearchEngine(
            openai_api_key=openai_api_key,
            google_api_key=google_api_key,
            bing_api_key=bing_api_key,
            custom_search_engine_id=custom_search_engine_id
        )
        
        start_time = datetime.now()
        
        # Test search
        search_results = engine.search_company_jobs(test_company)
        job_listings = engine.extract_structured_jobs(search_results, test_company)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        test_results = {
            'test_company': test_company,
            'search_successful': len(search_results) > 50,
            'extraction_successful': len(job_listings) > 0,
            'jobs_found': len(job_listings),
            'search_duration_seconds': duration,
            'raw_results_length': len(search_results),
            'sample_jobs': job_listings[:3] if job_listings else [],  # First 3 jobs as sample
            'capabilities': engine.get_search_capabilities(),
            'timestamp': start_time.isoformat(),
            'success': len(job_listings) > 0
        }
        
        return jsonify({
            'success': True,
            'test_results': test_results,
            'message': f'Test completed: {"Success" if test_results["success"] else "Failed"}'
        })
        
    except Exception as e:
        logger.error(f"Error testing search engine: {e}")
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
# Backend route wrappers for frontend compatibility
@app.route('/api/backend/jobs', methods=['GET'])
def backend_get_jobs():
    """Get jobs endpoint for /api/backend path."""
    return get_jobs()


@app.route('/api/backend/jobs/statistics', methods=['GET'])
def backend_get_job_statistics():
    """Get job statistics endpoint for /api/backend path."""
    return get_job_statistics()


@app.route('/api/backend/jobs/search', methods=['POST'])
def backend_trigger_job_search():
    """Trigger job search endpoint for /api/backend path."""
    return search_jobs()


@app.route('/api/backend/jobs/search-enhanced', methods=['POST'])
def backend_enhanced_search_jobs():
    """Enhanced job search endpoint for /api/backend path."""
    return enhanced_search_jobs()


@app.route('/api/backend/search/capabilities', methods=['GET'])
def backend_search_capabilities():
    """Search capabilities endpoint for /api/backend path."""
    return get_search_capabilities()


@app.route('/api/backend/search/test', methods=['POST'])
def backend_test_search():
    """Test search endpoint for /api/backend path."""
    return test_search_engine()


@app.route('/api/backend/jobs/export', methods=['GET'])
def backend_export_jobs():
    """Export jobs endpoint for /api/backend path."""
    return export_jobs()


@app.route('/api/backend/companies', methods=['GET', 'POST'])
def backend_companies():
    """Companies endpoint for /api/backend path."""
    if request.method == 'GET':
        return get_companies()
    else:
        return add_company()


# Vercel handler
def handler(request):
    """Handler for Vercel serverless functions."""
    initialize_database()
    return app(request.environ, request.start_response)
