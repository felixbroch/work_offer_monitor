#!/usr/bin/env python3
"""
Job Search Assistant - Main Entry Point

This is the main command-line interface for the Job Search Assistant.
It provides access to all major functionality through a simple menu system.
"""

import sys
import argparse
from pathlib import Path

# Import our modules
from src.core.job_search_engine import JobSearchEngine
from src.core.scheduler import JobSearchScheduler
from src.core.database import JobDatabase
from src.core.history_tracker import JobHistoryTracker
from config.config import OPENAI_SETTINGS


def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("Job Search Assistant")
    print("=" * 60)
    print("A comprehensive tool for automated job discovery and tracking")
    print()


def check_api_key():
    """Check if API key is configured."""
    api_key = OPENAI_SETTINGS.get("api_key")
    if not api_key or api_key == "your_openai_api_key_here":
        print("Error: OpenAI API key not configured.")
        print("Please set your API key in one of these ways:")
        print("   1. Create a .env file with OPENAI_API_KEY=your_key")
        print("   2. Set the OPENAI_API_KEY environment variable")
        print("   3. Get your API key from: https://platform.openai.com/api-keys")
        return False
    return True


def run_single_search():
    """Run a single job search."""
    print("Starting single job search...")
    
    api_key = OPENAI_SETTINGS["api_key"]
    engine = JobSearchEngine(api_key)
    engine.run()


def run_scheduler():
    """Run the job scheduler."""
    print("📅 Starting job scheduler...")
    
    api_key = OPENAI_SETTINGS["api_key"]
    scheduler = JobSearchScheduler(api_key)
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\n👋 Scheduler stopped by user")
        scheduler.stop_scheduler()


def run_once():
    """Run monitoring once."""
    print("Running monitoring once...")
    
    api_key = OPENAI_SETTINGS["api_key"]
    scheduler = JobSearchScheduler(api_key)
    scheduler.run_once()


def show_statistics():
    """Show job statistics."""
    print("Job Statistics:")
    print("-" * 40)
    
    try:
        db = JobDatabase()
        stats = db.get_job_statistics()
        
        print(f"Total jobs: {stats['total_jobs']}")
        print(f"Recent activity: {stats['recent_activity']}")
        print(f"New jobs today: {stats.get('new_jobs_today', 0)}")
        print()
        
        print("Status breakdown:")
        for status, count in stats['status_counts'].items():
            print(f"  {status}: {count}")
        print()
        
        print("Company breakdown:")
        for company, count in stats['company_counts'].items():
            print(f"  {company}: {count}")
        
    except Exception as e:
        print(f"Error getting statistics: {e}")


def launch_dashboard():
    """Launch the web application."""
    print("Launching web application...")
    
    try:
        import subprocess
        subprocess.run([sys.executable, "start_dev.py"])
    except Exception as e:
        print(f"Error launching web application: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Job Search Assistant - Automated job discovery and tracking"
    )
    parser.add_argument(
        "command",
        choices=["search", "schedule", "run-once", "stats", "dashboard"],
        help="Command to run"
    )
    
    # If no arguments provided, show interactive menu
    if len(sys.argv) == 1:
        print_banner()
        
        if not check_api_key():
            sys.exit(1)
        
        print("Choose an option:")
        print("1. Run single job search")
        print("2. Start scheduler (daily monitoring)")
        print("3. Run monitoring once")
        print("4. Show statistics")
        print("5. Launch dashboard")
        print("6. Exit")
        print()
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                run_single_search()
            elif choice == "2":
                run_scheduler()
            elif choice == "3":
                run_once()
            elif choice == "4":
                show_statistics()
            elif choice == "5":
                launch_dashboard()
            elif choice == "6":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Handle command-line arguments
        args = parser.parse_args()
        
        if not check_api_key():
            sys.exit(1)
        
        if args.command == "search":
            run_single_search()
        elif args.command == "schedule":
            run_scheduler()
        elif args.command == "run-once":
            run_once()
        elif args.command == "stats":
            show_statistics()
        elif args.command == "dashboard":
            launch_dashboard()


if __name__ == "__main__":
    main()
