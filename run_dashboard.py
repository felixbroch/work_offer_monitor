#!/usr/bin/env python3
"""
Dashboard Launcher for Job Search Assistant

Simple launcher script for the Streamlit dashboard.
"""

import subprocess
import sys
import os
from pathlib import Path

from config.config import DASHBOARD_SETTINGS


def main():
    """Launch the Streamlit dashboard."""
    dashboard_file = Path("src/dashboard/dashboard.py")
    
    if not dashboard_file.exists():
        print("Error: dashboard.py not found")
        sys.exit(1)
    
    # Get configuration
    host = DASHBOARD_SETTINGS.get("host", "localhost")
    port = DASHBOARD_SETTINGS.get("port", 8501)
    
    print("Starting Job Search Assistant Dashboard...")
    print(f"📍 URL: http://{host}:{port}")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_file),
            "--server.address", host,
            "--server.port", str(port),
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 