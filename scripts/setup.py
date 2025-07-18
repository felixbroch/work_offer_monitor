#!/usr/bin/env python3
"""
Setup Script for Job Search Assistant

This script helps set up the Job Search Assistant with proper configuration.
"""

import os
import sys
from pathlib import Path
import shutil
import subprocess

# Add the parent directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("Job Search Assistant Setup")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 10):
        print("Error: Python 3.10 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"Python version: {sys.version}")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def setup_environment():
    """Set up environment configuration."""
    print("Setting up environment...")
    
    env_template = Path("config/.env.template")
    env_file = Path("config/.env")
    
    if not env_template.exists():
        print("Error: config/.env.template not found")
        return False
    
    if env_file.exists():
        print(".env file already exists")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            print("Skipping environment setup")
            return True
    
    # Copy template to .env
    shutil.copy(env_template, env_file)
    print("Created .env file from template")
    
    # Prompt for API key
    print("\nAPI Key Configuration:")
    print("You need an OpenAI API key to use this tool.")
    print("Get one from: https://platform.openai.com/api-keys")
    print()
    
    api_key = input("Enter your OpenAI API key (or press Enter to configure later): ").strip()
    
    if api_key:
        # Update .env file with API key
        with open(env_file, 'r') as f:
            content = f.read()
        
        content = content.replace(
            "OPENAI_API_KEY=your_openai_api_key_here",
            f"OPENAI_API_KEY={api_key}"
        )
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("API key configured in .env file")
    else:
        print("API key not configured. You can add it to .env later.")
    
    return True


def setup_companies():
    """Set up companies to monitor."""
    print("Setting up companies to monitor...")
    
    companies_file = Path("data/companies_to_watch.csv")
    
    if companies_file.exists():
        print("Companies file already exists")
        with open(companies_file, 'r') as f:
            lines = f.readlines()
            company_count = len(lines) - 1  # Subtract header
            print(f"   Found {company_count} companies configured")
    else:
        print("Companies file not found. Creating default...")
        
        # Ensure data directory exists
        companies_file.parent.mkdir(parents=True, exist_ok=True)
        
        default_companies = """company_name,career_page_url
Google,https://careers.google.com/jobs/results/
Microsoft,https://careers.microsoft.com/us/en/search-results
Amazon,https://amazon.jobs/en/search
"""
        
        with open(companies_file, 'w') as f:
            f.write(default_companies)
        
        print("Created default companies file")
    
    return True


def setup_config():
    """Set up configuration."""
    print("Configuration setup...")
    
    config_file = Path("config/config.py")
    
    if config_file.exists():
        print("Configuration file exists")
        
        # Check if it looks properly configured
        with open(config_file, 'r') as f:
            content = f.read()
            
            if "your_openai_api_key_here" in content:
                print("Configuration may need updating")
                print("   Please check config/config.py for any placeholder values")
    else:
        print("Configuration file not found")
        return False
    
    return True


def run_test():
    """Run a simple test to verify setup."""
    print("Running setup verification...")
    
    try:
        # Add the parent directory to Python path for imports
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Test imports
        from config.config import OPENAI_SETTINGS, FILTERING_CRITERIA
        print("Configuration imports successful")
        
        # Test API key
        api_key = OPENAI_SETTINGS.get("api_key")
        if api_key and api_key != "your_openai_api_key_here":
            print("API key configured")
        else:
            print("API key not configured or using placeholder")
        
        # Test database creation
        from src.core.database import JobDatabase
        db = JobDatabase(":memory:")  # In-memory test database
        print("Database functionality working")
        
        return True
        
    except Exception as e:
        print(f"Setup verification failed: {e}")
        return False


def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Setup companies
    if not setup_companies():
        sys.exit(1)
    
    # Setup configuration
    if not setup_config():
        sys.exit(1)
    
    # Run test
    if not run_test():
        print("Setup completed with warnings")
    else:
        print("Setup completed successfully!")
    
    print("\n" + "=" * 60)
    print("Job Search Assistant is ready to use!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review and customise companies_to_watch.csv")
    print("2. Adjust search criteria in config.py")
    print("3. Run: python main.py")
    print("4. Or launch dashboard: python run_dashboard.py")
    print()
    print("For help, see README.md or run: python main.py")


if __name__ == "__main__":
    main()
