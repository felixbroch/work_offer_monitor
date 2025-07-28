# Ultra-Minimal Job Search API

This is a completely isolated, minimal API directory designed to deploy on Vercel without hitting the 250MB size limit.

## Structure
- `api/index.py` - Ultra-minimal Flask API with OpenAI integration
- `requirements.txt` - Only 2 dependencies: openai + flask (~20MB total)
- `vercel.json` - Vercel configuration

## Deployment
1. `cd vercel-api`
2. `vercel deploy`

## Total Size
- openai==1.97.1 (~15MB)
- flask==3.0.3 (~5MB)
- **Total: ~20MB (well under 250MB limit)**

## Features
- Health check endpoint
- Enhanced job search with OpenAI
- Test search functionality
- Basic company management
- Full CORS support
