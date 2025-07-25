import sys
import os
import time
from flask import Flask, jsonify, request

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Create Flask app
app = Flask(__name__)

# Add CORS
@app.after_request  
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Simple health check
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'API is running'})

# Mock endpoints for testing - replace with real implementation once working
@app.route('/api/backend/jobs')
def get_jobs():
    return jsonify({
        'jobs': [],
        'message': 'Jobs endpoint working'
    })

@app.route('/api/backend/jobs/statistics')
def get_statistics():
    return jsonify({
        'total_jobs': 0,
        'recent_activity': 0,
        'status_counts': {},
        'company_counts': {},
        'message': 'Statistics endpoint working'
    })

@app.route('/api/backend/jobs/search', methods=['POST'])
def search_jobs():
    return jsonify({
        'message': 'Search endpoint working',
        'status': 'success'
    })

@app.route('/api/backend/jobs/search-with-criteria', methods=['POST'])
def search_jobs_with_criteria():
    """Search for jobs using OpenAI agent with custom criteria."""
    try:
        data = request.get_json() or {}
        api_key = data.get('api_key')
        criteria = data.get('criteria', {})
        companies = data.get('companies', [])
        
        if not api_key:
            return jsonify({'success': False, 'error': 'API key required'}), 400
        
        if not companies:
            return jsonify({'success': False, 'error': 'Companies list required'}), 400
        
        # Return simple mock data for now
        mock_jobs = [
            {
                'title': 'Software Engineer',
                'company_name': companies[0] if companies else 'Test Company',
                'location': 'San Francisco, CA',
                'url': 'https://example.com/job',
                'description': 'Test job description from Python backend',
                'experience_level': 'senior',
                'salary_range': '$100k-150k',
                'posting_date': '2024-01-15',
                'search_method': 'PYTHON_MOCK',
                'job_id': 'python-test-1'
            }
        ]
        
        return jsonify({
            'success': True,
            'jobs': mock_jobs,
            'companies_searched': len(companies),
            'companies_with_results': 1,
            'search_method': 'PYTHON_BACKEND_MOCK',
            'total_jobs': len(mock_jobs),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}',
            'jobs': [],
            'search_method': 'ERROR'
        }), 500

@app.route('/api/backend/companies', methods=['GET', 'POST'])
def handle_companies():
    if request.method == 'GET':
        return jsonify({
            'companies': [
                {
                    'id': 1,
                    'name': 'Tech Corp',
                    'domain': 'techcorp.com',
                    'industry': 'Technology',
                    'size': 'Large',
                    'jobs_posted': 15,
                    'last_activity': '2024-01-15',
                    'status': 'active'
                },
                {
                    'id': 2,
                    'name': 'StartupXYZ',
                    'domain': 'startupxyz.com',
                    'industry': 'Fintech',
                    'size': 'Small',
                    'jobs_posted': 3,
                    'last_activity': '2024-01-10',
                    'status': 'active'
                }
            ],
            'total': 2,
            'active': 2,
            'message': 'Companies retrieved successfully'
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json() or {}
            name = data.get('name', '')
            domain = data.get('domain', '')
            industry = data.get('industry', 'Unknown')
            size = data.get('size', 'Unknown')
            
            if not name or not domain:
                return jsonify({
                    'error': 'Name and domain are required'
                }), 400
            
            # Mock creating a new company
            new_company = {
                'id': int(time.time()),  # Simple ID generation
                'name': name,
                'domain': domain,
                'industry': industry,
                'size': size,
                'jobs_posted': 0,
                'last_activity': time.strftime('%Y-%m-%d'),
                'status': 'active'
            }
            
            return jsonify(new_company), 201
            
        except Exception as e:
            return jsonify({
                'error': f'Failed to create company: {str(e)}'
            }), 500

@app.route('/api/backend/validate-api-key', methods=['POST'])
def validate_api_key():
    data = request.get_json() or {}
    api_key = data.get('api_key', '')
    
    if api_key.startswith('sk-') and len(api_key) > 20:
        return jsonify({
            'valid': True,
            'message': 'API key is valid'
        })
    else:
        return jsonify({
            'valid': False,
            'message': 'Invalid API key format'
        }), 400

@app.route('/api/backend/jobs/export', methods=['POST'])
def export_jobs():
    try:
        data = request.get_json() or {}
        format_type = data.get('format', 'csv')
        jobs = data.get('jobs', [])
        
        if not jobs:
            return jsonify({'error': 'No jobs to export'}), 400
            
        if format_type == 'json':
            return jsonify({
                'jobs': jobs,
                'exported_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'total_jobs': len(jobs)
            })
        else:
            # For CSV, we'd need to create the actual CSV content
            # For now, just return success message
            return jsonify({
                'message': 'Export feature coming soon',
                'format': format_type,
                'jobs_count': len(jobs)
            })
            
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

# Fallback for all other routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def fallback(path):
    return jsonify({
        'error': 'Endpoint not found',
        'path': path,
        'available_endpoints': [
            '/api/health',
            '/api/backend/jobs',
            '/api/backend/jobs/statistics', 
            '/api/backend/jobs/search',
            '/api/backend/jobs/search-with-criteria',
            '/api/backend/jobs/export',
            '/api/backend/companies',
            '/api/backend/validate-api-key'
        ]
    }), 404
