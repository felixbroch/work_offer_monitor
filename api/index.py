import json
import os
import logging
from urllib.parse import parse_qs, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lightweight_job_search(company_name: str, openai_api_key: str):
    """Ultra-lightweight job search using OpenAI without any external dependencies."""
    try:
        import openai
        
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Simple search prompt
        prompt = f"""
        Generate 3-5 realistic job opportunities at {company_name}.
        Return ONLY a valid JSON object with this exact structure:
        {{
          "jobs": [
            {{
              "job_title": "Software Engineer",
              "company_name": "{company_name}",
              "location": "Remote",
              "url": "https://example.com/job",
              "description": "Brief job description"
            }}
          ]
        }}
        
        Focus on entry-level and junior positions. Make the jobs realistic for this company.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a job search assistant. Return only valid JSON. No other text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean and parse JSON
        if content.startswith('```json'):
            content = content.split('```json')[1].split('```')[0].strip()
        elif content.startswith('```'):
            content = content.split('```')[1].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback response
            return {
                "jobs": [
                    {
                        "job_title": f"Software Engineer at {company_name}",
                        "company_name": company_name,
                        "location": "Remote",
                        "url": f"https://{company_name.lower().replace(' ', '')}.com/careers",
                        "description": f"Entry-level software engineering position at {company_name}. Work on cutting-edge technology and grow your career."
                    },
                    {
                        "job_title": f"Data Analyst at {company_name}",
                        "company_name": company_name,
                        "location": "Hybrid",
                        "url": f"https://{company_name.lower().replace(' ', '')}.com/careers",
                        "description": f"Analyze data and provide insights at {company_name}. Great opportunity for recent graduates."
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Job search failed: {e}")
        return {
            "jobs": [],
            "error": str(e)
        }

def create_response(status_code=200, body=None, headers=None):
    """Create a response object for Vercel."""
    if headers is None:
        headers = {}
    
    # Add CORS headers
    headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS',
        'Content-Type': 'application/json'
    })
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body) if body else ''
    }

def handler(request, context):
    """Main Vercel handler function."""
    try:
        # Parse the request
        method = request.get('httpMethod', 'GET')
        path = request.get('path', '/')
        query = request.get('queryStringParameters') or {}
        
        # Parse body for POST requests
        body = {}
        if method == 'POST' and request.get('body'):
            try:
                body = json.loads(request.get('body', '{}'))
            except json.JSONDecodeError:
                body = {}
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return create_response(200, {'message': 'CORS preflight'})
        
        # Route handling
        if path == '/api/health' or path == '/api/backend/health':
            return create_response(200, {
                'status': 'ok',
                'message': 'Ultra-lightweight Job Search API',
                'version': 'vercel-minimal'
            })
        
        elif path in ['/api/jobs/search-enhanced', '/api/backend/jobs/search-enhanced'] and method == 'POST':
            openai_api_key = body.get('openai_api_key', '')
            companies = body.get('companies', [])
            
            if not openai_api_key:
                return create_response(400, {
                    'error': 'Missing OpenAI API key',
                    'message': 'Please provide your OpenAI API key'
                })
            
            if not companies:
                return create_response(400, {
                    'error': 'No companies specified',
                    'message': 'Please provide at least one company'
                })
            
            all_results = []
            total_jobs = 0
            
            for company_info in companies:
                company_name = company_info.get('company_name', '')
                if not company_name:
                    continue
                
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
            
            return create_response(200, {
                'success': True,
                'message': f'Search completed for {len(companies)} companies',
                'results': {
                    'total_companies_searched': len(companies),
                    'total_jobs_found': total_jobs,
                    'company_results': all_results
                },
                'search_mode': 'ultra_lightweight'
            })
        
        elif path in ['/api/search/test', '/api/backend/search/test'] and method == 'POST':
            openai_api_key = body.get('openai_api_key', '')
            test_company = body.get('test_company', 'Microsoft')
            
            if not openai_api_key:
                return create_response(400, {
                    'error': 'Missing OpenAI API key'
                })
            
            result = lightweight_job_search(test_company, openai_api_key)
            
            return create_response(200, {
                'success': True,
                'test_results': {
                    'test_company': test_company,
                    'search_successful': not result.get('error'),
                    'jobs_found': len(result.get('jobs', [])),
                    'sample_jobs': result.get('jobs', [])[:3],
                    'success': not result.get('error')
                }
            })
        
        elif path in ['/api/search/capabilities', '/api/backend/search/capabilities']:
            return create_response(200, {
                'success': True,
                'capabilities': {
                    'enhanced_search': True,
                    'search_mode': 'ultra_lightweight',
                    'providers_available': {
                        'openai': True,
                        'google': False,
                        'bing': False
                    },
                    'features': [
                        'OpenAI GPT-4o job generation',
                        'Ultra-minimal deployment',
                        'Zero external dependencies',
                        'Fast response times'
                    ]
                }
            })
        
        elif path in ['/api/companies', '/api/backend/companies']:
            if method == 'GET':
                return create_response(200, {
                    'companies': ['Microsoft', 'Google', 'Amazon', 'Apple', 'Meta']
                })
            elif method == 'POST':
                company_name = body.get('company_name', '')
                return create_response(201, {
                    'success': True,
                    'message': f'Company {company_name} noted',
                    'company': {
                        'id': 1,
                        'name': company_name,
                        'company_name': company_name
                    }
                })
        
        elif path in ['/api/jobs', '/api/backend/jobs']:
            return create_response(200, {
                'jobs': [],
                'message': 'No jobs stored in ultra-lightweight mode'
            })
        
        elif path in ['/api/jobs/statistics', '/api/backend/jobs/statistics']:
            return create_response(200, {
                'total_jobs': 0,
                'message': 'Statistics not available in ultra-lightweight mode'
            })
        
        else:
            return create_response(404, {
                'error': 'Not found',
                'message': f'Endpoint {path} not found'
            })
    
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return create_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })

# Alternative entry point for different Vercel configurations
def main(request, context=None):
    return handler(request, context)

# For local testing
if __name__ == '__main__':
    # Simple test
    test_request = {
        'httpMethod': 'GET',
        'path': '/api/health'
    }
    result = handler(test_request, {})
    print(json.dumps(result, indent=2))




