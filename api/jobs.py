"""
Jobs API endpoint for Vercel serverless functions
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.api.server import app, initialize_database

# Initialize database
try:
    initialize_database()
except Exception as e:
    print(f"Database initialization error: {e}")

# This is the entry point for /api/jobs
def handler(request):
    return app(request.environ, request.start_response)

# For direct Flask compatibility
if __name__ == '__main__':
    app.run()
