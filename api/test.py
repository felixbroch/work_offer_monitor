from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'API is running',
        'environment': {
            'python_path': os.sys.path[0:3],
            'working_directory': os.getcwd(),
            'env_vars': {
                'DATABASE_PATH': os.environ.get('DATABASE_PATH', 'not set'),
                'OPENAI_API_KEY': 'set' if os.environ.get('OPENAI_API_KEY') else 'not set'
            }
        }
    })

@app.route('/test')
def test():
    """Test endpoint."""
    return jsonify({'message': 'Test successful'})

if __name__ == '__main__':
    app.run(debug=True)
