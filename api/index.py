import sys
import os
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
        data = request.get_json()
        api_key = data.get('api_key')
        criteria = data.get('criteria', {})
        companies = data.get('companies', [])
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 400
        
        if not companies:
            return jsonify({'error': 'Companies list required'}), 400
        
        # Import here to avoid circular imports
        from src.core.advanced_job_agent import OpenAIJobSearchAgent
        
        # Create agent with API key
        agent = OpenAIJobSearchAgent(api_key)
        
        all_jobs = []
        search_results = []
        
        for company in companies:
            company_name = company.get('company_name', '')
            career_url = company.get('career_page_url', '')
            
            if not company_name:
                continue
                
            try:
                # Search with custom criteria
                jobs = agent.search_company_jobs(company_name, career_url, criteria)
                all_jobs.extend(jobs)
                
                search_results.append({
                    'company': company_name,
                    'jobs_found': len(jobs),
                    'status': 'success'
                })
                
            except Exception as e:
                search_results.append({
                    'company': company_name,
                    'jobs_found': 0,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'jobs': all_jobs,
            'total_jobs': len(all_jobs),
            'search_results': search_results,
            'criteria_used': criteria,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Search failed: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/backend/companies')
def get_companies():
    return jsonify({
        'companies': [],
        'message': 'Companies endpoint working'
    })

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
            '/api/backend/companies',
            '/api/backend/validate-api-key'
        ]
    }), 404
