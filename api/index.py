import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.api.server import app, initialize_database

# Initialize the database when the module is imported
initialize_database()

# Export the app for Vercel
def handler(request):
    return app
