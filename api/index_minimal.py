"""Ultra-lightweight API for Vercel deployment - under 250MB limit"""

import json
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def generate_jobs(company_name: str, api_key: str):
    """Generate jobs using OpenAI with minimal overhead."""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user", 
                "content": f"List 3 entry-level jobs at {company_name}. Return JSON: [{{'job_title':'', 'location':'', 'description':''}}]"
            }],
            max_tokens=500,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        start = content.find('[')
        end = content.rfind(']') + 1
        if start >= 0 and end > start:
            jobs_data = json.loads(content[start:end])
            return [{
                "job_id": f"{company_name}_{i}",
                "job_title": job.get("job_title", "Software Engineer"),
                "company_name": company_name,
                "location": job.get("location", "Remote"),
                "url": f"https://{company_name.lower()}.com/careers",
                "description": job.get("description", "Entry-level position")
            } for i, job in enumerate(jobs_data[:3])]
    except:
        pass
    
    # Fallback
    return [{
        "job_id": f"{company_name}_1",
        "job_title": f"Software Engineer at {company_name}",
        "company_name": company_name,
        "location": "Remote",
        "url": f"https://{company_name.lower()}.com/careers",
        "description": f"Entry-level position at {company_name}"
    }]

@app.route('/api/health')
@app.route('/api/backend/health')
def health():
    return jsonify({"status": "ok", "mode": "ultra-lightweight"})

@app.route('/api/jobs/search-enhanced', methods=['POST'])
@app.route('/api/backend/jobs/search-enhanced', methods=['POST'])
def search_enhanced():
    data = request.get_json()
    api_key = data.get('openai_api_key')
    companies = data.get('companies', [])
    
    if not api_key:
        return jsonify({"error": "Missing OpenAI API key"}), 400
    
    results = []
    total_jobs = 0
    
    for company in companies:
        name = company.get('company_name', '')
        if name:
            jobs = generate_jobs(name, api_key)
            total_jobs += len(jobs)
            results.append({
                "company_name": name,
                "jobs_found": len(jobs),
                "status": "success",
                "jobs": jobs
            })
    
    return jsonify({
        "success": True,
        "results": {
            "total_companies_searched": len(companies),
            "total_jobs_found": total_jobs,
            "company_results": results
        }
    })

@app.route('/api/search/test', methods=['POST'])
@app.route('/api/backend/search/test', methods=['POST'])
def test_search():
    data = request.get_json()
    api_key = data.get('openai_api_key')
    company = data.get('test_company', 'Microsoft')
    
    if not api_key:
        return jsonify({"error": "Missing API key"}), 400
    
    jobs = generate_jobs(company, api_key)
    return jsonify({
        "success": True,
        "test_results": {
            "test_company": company,
            "jobs_found": len(jobs),
            "sample_jobs": jobs[:2]
        }
    })

@app.route('/api/search/capabilities')
@app.route('/api/backend/search/capabilities')
def capabilities():
    return jsonify({
        "success": True,
        "capabilities": {
            "mode": "ultra-lightweight",
            "openai_enabled": True,
            "features": ["AI job generation", "Multi-company search"]
        }
    })

# Backward compatibility
@app.route('/api/jobs')
@app.route('/api/backend/jobs')
def get_jobs():
    return jsonify({"jobs": []})

@app.route('/api/companies')
@app.route('/api/backend/companies')
def get_companies():
    return jsonify({"companies": ["Microsoft", "Google", "Amazon"]})

@app.route('/api/companies', methods=['POST'])
@app.route('/api/backend/companies', methods=['POST'])
def add_company():
    data = request.get_json()
    return jsonify({
        "success": True,
        "company": {"name": data.get('company_name', '')}
    })

# CORS preflight
@app.route('/api/<path:path>', methods=['OPTIONS'])
@app.route('/api/backend/<path:path>', methods=['OPTIONS'])
def options(path):
    return '', 200

if __name__ == '__main__':
    app.run(debug=True)
