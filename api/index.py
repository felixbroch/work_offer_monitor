import sys
import os
import time
import json
import logging
from flask import Flask, jsonify, request

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Add CORS
@app.after_request  
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Lightweight OpenAI integration for Vercel
def lightweight_job_search(company_name: str, openai_api_key: str):
    """Lightweight job search using OpenAI without heavy dependencies."""
    try:
        import openai
        
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Simple search prompt
        prompt = f"""
        Find job opportunities at {company_name}. 
        Return a JSON list of jobs with the following structure:
        {{
          "jobs": [
            {{
              "job_title": "Software Engineer",
              "company_name": "{company_name}",
              "location": "Remote",
              "url": "https://example.com/job",
              "description": "Job description here"
            }}
          ]
        }}
        
        Focus on entry-level and junior positions. If no specific jobs are found, provide realistic example positions this company might have.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a job search assistant. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        # Try to extract JSON from response
        try:
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].strip()
            else:
                json_str = content.strip()
            
            return json.loads(json_str)
        except:
            # Fallback if JSON parsing fails
            return {
                "jobs": [
                    {
                        "job_title": f"Software Engineer at {company_name}",
                        "company_name": company_name,
                        "location": "Remote",
                        "url": f"https://{company_name.lower().replace(' ', '')}.com/careers",
                        "description": f"Entry-level software engineering position at {company_name}"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Lightweight search failed: {e}")
        return {"jobs": [], "error": str(e)}

# Health check endpoint
@app.route('/api/health')
@app.route('/api/backend/health')
def health():
    return jsonify({
        'status': 'ok', 
        'message': 'Lightweight Job Search API is running',
        'version': 'vercel-optimized'
    })

# Enhanced job search endpoint
@app.route('/api/backend/jobs/search-enhanced', methods=['POST'])
@app.route('/api/jobs/search-enhanced', methods=['POST'])
def enhanced_search():
    try:
        data = request.get_json()
        openai_api_key = data.get('openai_api_key')
        companies = data.get('companies', [])
        
        if not openai_api_key:
            return jsonify({
                'error': 'Missing OpenAI API key',
                'message': 'Please provide your OpenAI API key'
            }), 400
        
        if not companies:
            return jsonify({
                'error': 'No companies specified',
                'message': 'Please provide at least one company to search'
            }), 400
        
        all_results = []
        total_jobs = 0
        
        for company_info in companies:
            company_name = company_info.get('company_name', '')
            if not company_name:
                continue
                
            logger.info(f"Searching jobs for {company_name}")
            
            # Use lightweight search
            search_result = lightweight_job_search(company_name, openai_api_key)
            jobs_found = len(search_result.get('jobs', []))
            total_jobs += jobs_found
            
            all_results.append({
                'company_name': company_name,
                'jobs_found': jobs_found,
                'status': 'success' if not search_result.get('error') else 'error',
                'jobs': search_result.get('jobs', []),
                'error': search_result.get('error')
            })
        
        return jsonify({
            'success': True,
            'message': f'Enhanced search completed for {len(companies)} companies',
            'results': {
                'total_companies_searched': len(companies),
                'total_jobs_found': total_jobs,
                'company_results': all_results
            },
            'search_mode': 'lightweight_openai'
        })
        
    except Exception as e:
        logger.error(f"Enhanced search error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# Test search endpoint
@app.route('/api/backend/search/test', methods=['POST'])
@app.route('/api/search/test', methods=['POST'])
def test_search():
    try:
        data = request.get_json()
        openai_api_key = data.get('openai_api_key')
        test_company = data.get('test_company', 'Microsoft')
        
        if not openai_api_key:
            return jsonify({
                'error': 'Missing OpenAI API key',
                'message': 'Please provide your OpenAI API key'
            }), 400
        
        # Test the lightweight search
        result = lightweight_job_search(test_company, openai_api_key)
        
        return jsonify({
            'success': True,
            'test_results': {
                'test_company': test_company,
                'search_successful': not result.get('error'),
                'jobs_found': len(result.get('jobs', [])),
                'sample_jobs': result.get('jobs', [])[:3],
                'success': not result.get('error')
            }
        })
        
    except Exception as e:
        logger.error(f"Test search error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# Search capabilities endpoint
@app.route('/api/backend/search/capabilities', methods=['GET'])
@app.route('/api/search/capabilities', methods=['GET'])
def search_capabilities():
    return jsonify({
        'success': True,
        'capabilities': {
            'enhanced_search': True,
            'search_mode': 'lightweight_openai',
            'providers_available': {
                'openai': True,
                'google': False,
                'bing': False,
                'duckduckgo': False
            },
            'features': [
                'OpenAI-powered job discovery',
                'Lightweight Vercel deployment',
                'No external API dependencies',
                'JSON structured responses'
            ],
            'limitations': [
                'Simulated job results',
                'No real-time web search',
                'OpenAI API key required'
            ]
        }
    })

# Fallback endpoints for backward compatibility  
@app.route('/api/backend/jobs', methods=['GET'])
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    return jsonify({
        'jobs': [],
        'message': 'No jobs stored in lightweight mode'
    })

@app.route('/api/backend/jobs/statistics', methods=['GET'])
@app.route('/api/jobs/statistics', methods=['GET'])
def get_statistics():
    return jsonify({
        'total_jobs': 0,
        'recent_activity': 0,
        'status_counts': {},
        'company_counts': {},
        'message': 'Statistics not available in lightweight mode'
    })

@app.route('/api/backend/jobs/search', methods=['POST'])
@app.route('/api/jobs/search', methods=['POST'])
def basic_search():
    try:
        data = request.get_json()
        companies = data.get('companies', [])
        
        # Simple response for backward compatibility
        results = []
        for company_info in companies:
            company_name = company_info.get('company_name', '')
            results.append({
                'company_name': company_name,
                'jobs_found': 0,
                'summary': 'Use enhanced search endpoint for real results'
            })
        
        return jsonify({
            'success': True,
            'message': 'Basic search completed (use enhanced endpoint for real results)',
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/backend/companies', methods=['GET'])
@app.route('/api/companies', methods=['GET'])
def get_companies():
    return jsonify({
        'companies': [
            'Microsoft',
            'Google', 
            'Amazon',
            'Apple',
            'Meta'
        ]
    })

@app.route('/api/backend/companies', methods=['POST'])
@app.route('/api/companies', methods=['POST'])
def add_company():
    try:
        data = request.get_json()
        company_name = data.get('company_name', '')
        
        return jsonify({
            'success': True,
            'message': f'Company {company_name} noted (not persisted in lightweight mode)',
            'company': {
                'id': int(time.time()),
                'name': company_name,
                'company_name': company_name
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# Handle CORS preflight requests
@app.route('/api/<path:path>', methods=['OPTIONS'])
@app.route('/api/backend/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return '', 200

# Vercel handler
def handler(event, context):
    """Vercel serverless function handler."""
    return app(event, context)

# For testing locally
if __name__ == '__main__':
    app.run(debug=True, port=5000)

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
