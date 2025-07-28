#!/usr/bin/env python3
"""
Quick Start Script for Enhanced Job Search Assistant

This script helps you quickly start the enhanced backend server.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main function to start the enhanced backend."""
    
    print("🚀 Enhanced Job Search Assistant - Quick Start")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Check if .env file exists
    env_file = project_root / "config" / ".env"
    if not env_file.exists():
        print("❌ Configuration file not found!")
        print("Please run setup first:")
        print("   python scripts/enhanced_setup.py")
        return False
    
    # Check if virtual environment is active
    if not sys.prefix != sys.base_prefix:
        print("⚠️  Virtual environment not detected")
        print("Recommended: Activate your virtual environment first")
        print()
    
    # Start the Flask server
    server_path = project_root / "backend" / "api" / "server.py"
    
    if not server_path.exists():
        print(f"❌ Server file not found: {server_path}")
        return False
    
    print("🔧 Starting Enhanced Flask API Server...")
    print(f"📂 Server location: {server_path}")
    print("🌐 Server will be available at: http://localhost:5000")
    print()
    print("Available endpoints:")
    print("  • GET  /api/health - Health check")
    print("  • POST /api/jobs/search-enhanced - Enhanced job search")
    print("  • GET  /api/search/capabilities - Search capabilities")
    print("  • POST /api/search/test - Test search engine")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Change to project directory
        os.chdir(project_root)
        
        # Start the server
        result = subprocess.run([
            sys.executable, str(server_path)
        ], check=True)
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
