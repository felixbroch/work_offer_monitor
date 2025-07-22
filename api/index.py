import sys
import os
import logging

# Configure logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.api.server import app, initialize_database
    
    # Initialize the database when the module is imported
    initialize_database()
    logger.info("Database initialized successfully")
    
except Exception as e:
    logger.error(f"Error during initialization: {e}")
    # Create a minimal Flask app for error handling
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def fallback(path):
        return jsonify({
            'error': 'Service initialization failed',
            'message': str(e)
        }), 500

# Export the Flask app directly for Vercel
# This is the WSGI application that Vercel will use
