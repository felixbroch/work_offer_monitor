#!/usr/bin/env python3
"""
Development Server Startup Script

This script starts both the Python API backend and Next.js frontend
for local development.
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import openai
        print("✓ Python dependencies found")
    except ImportError as e:
        print(f"✗ Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check if Node.js dependencies exist
    if not Path("node_modules").exists():
        print("✗ Node.js dependencies not found")
        print("Please run: npm install")
        return False
    
    print("✓ Node.js dependencies found")
    return True

def start_backend():
    """Start the Python API backend."""
    print("Starting Python API backend...")
    return subprocess.Popen([
        sys.executable, "backend/api/server.py"
    ], cwd=os.getcwd())

def start_frontend():
    """Start the Next.js frontend."""
    print("Starting Next.js frontend...")
    return subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=os.getcwd())

def main():
    """Main function to start development servers."""
    print("=" * 60)
    print("Job Search Assistant - Development Server")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check for environment file
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚠️  Warning: .env file not found")
        print("Please copy .env.example to .env and configure your settings")
        if input("Continue anyway? (y/N): ").lower() != 'y':
            sys.exit(1)
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        processes.append(backend_process)
        time.sleep(3)  # Give backend time to start
        
        # Start frontend
        frontend_process = start_frontend()
        processes.append(frontend_process)
        
        print("\n" + "=" * 60)
        print("Development servers started successfully!")
        print("=" * 60)
        print("Frontend: http://localhost:3000")
        print("Backend API: http://localhost:5000")
        print("\nPress Ctrl+C to stop all servers")
        print("=" * 60)
        
        # Wait for processes
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n\nStopping development servers...")
        for process in processes:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("All servers stopped.")
    
    except Exception as e:
        print(f"\nError starting servers: {e}")
        for process in processes:
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
