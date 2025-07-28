"""Ultra-minimal API for Vercel deployment - isolated from main project"""
import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Manual CORS handling to avoid flask-cors dependency
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def generate_sample_jobs(company_name: str, api_key: str = None):
    """Generate sample jobs using OpenAI (minimal implementation)."""
    try:
        if api_key:
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Use cheaper model
                messages=[
                    {"role": "system", "content": "Generate 3-5 realistic job postings for the given company. Return only valid JSON."},
                    {"role": "user", "content": f"Create job listings for {company_name}. Format: {{\"jobs\": [{{\"job_title\": \"...\", \"company_name\": \"{company_name}\", \"location\": \"...\", \"description\": \"...\"}}]}}"}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content.split('```json')[1].split('```')[0].strip()
            elif content.startswith('```'):
                content = content.split('```')[1].strip()
            
            return json.loads(content)
    except:
        pass
    
    # Fallback sample jobs
    return {
        "jobs": [
            {
                "job_title": f"Software Engineer at {company_name}",
                "company_name": company_name,
                "location": "Remote",
                "description": f"Software engineering position at {company_name}. Entry to mid-level opportunity."
            },
            {
                "job_title": f"Data Analyst at {company_name}",
                "company_name": company_name,
                "location": "Remote/Hybrid",
                "description": f"Data analysis role at {company_name}. Work with large datasets and business intelligence."
            }
        ]
    }

@app.route('/api/health')
@app.route('/api/backend/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Ultra-minimal API running'})

@app.route('/api/jobs/search-enhanced', methods=['POST'])
@app.route('/api/backend/jobs/search-enhanced', methods=['POST'])
def enhanced_search():
    try:
        data = request.get_json() or {}
        api_key = data.get('openai_api_key')
        companies = data.get('companies', [])
        
        if not companies:
            return jsonify({'error': 'No companies specified'}), 400
        
        results = []
        total_jobs = 0
        
        for company_info in companies:
            company_name = company_info.get('company_name', '')
            if not company_name:
                continue
                
            job_data = generate_sample_jobs(company_name, api_key)
            jobs = job_data.get('jobs', [])
            total_jobs += len(jobs)
            
            results.append({
                'company_name': company_name,
                'jobs_found': len(jobs),
                'status': 'success',
                'jobs': jobs
            })
        
        return jsonify({
            'success': True,
            'message': f'Search completed for {len(companies)} companies',
            'results': {
                'total_companies_searched': len(companies),
                'total_jobs_found': total_jobs,
                'company_results': results
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/test', methods=['POST'])
@app.route('/api/backend/search/test', methods=['POST'])
def test_search():
    try:
        data = request.get_json() or {}
        api_key = data.get('openai_api_key')
        test_company = data.get('test_company', 'Microsoft')
        
        result = generate_sample_jobs(test_company, api_key)
        jobs = result.get('jobs', [])
        
        return jsonify({
            'success': True,
            'test_results': {
                'test_company': test_company,
                'jobs_found': len(jobs),
                'sample_jobs': jobs[:2],
                'success': len(jobs) > 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/capabilities')
@app.route('/api/backend/search/capabilities')
def capabilities():
    return jsonify({
        'success': True,
        'capabilities': {
            'enhanced_search': True,
            'search_mode': 'ultra_minimal',
            'providers_available': {'openai': True},
            'features': ['OpenAI job generation', 'Minimal deployment']
        }
    })

@app.route('/api/jobs')
@app.route('/api/backend/jobs')
def get_jobs():
    return jsonify({'jobs': [], 'message': 'Minimal mode - no storage'})

@app.route('/api/companies', methods=['GET'])
@app.route('/api/backend/companies', methods=['GET'])
def get_companies():
    return jsonify({'companies': ['Microsoft', 'Google', 'Amazon', 'Apple']})

@app.route('/api/companies', methods=['POST'])
@app.route('/api/backend/companies', methods=['POST'])
def add_company():
    try:
        data = request.get_json() or {}
        company_name = data.get('company_name', '')
        return jsonify({
            'success': True,
            'message': f'Company {company_name} noted',
            'company': {'name': company_name, 'company_name': company_name}
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# CORS preflight
@app.route('/api/<path:path>', methods=['OPTIONS'])
@app.route('/api/backend/<path:path>', methods=['OPTIONS'])
def options(path):
    return '', 200

# Vercel handler
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)
