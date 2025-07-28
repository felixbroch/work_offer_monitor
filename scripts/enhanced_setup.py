#!/usr/bin/env python3
"""
Enhanced Setup Script for Job Search Assistant

This script helps configure the enhanced job search system with real web search capabilities.
It guides users through API key setup and tests the search functionality.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional
import requests

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.config import load_env_file
from src.core.enhanced_job_search_engine import EnhancedJobSearchEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedSetupManager:
    """Manager for setting up the enhanced job search system."""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.env_file = self.config_dir / ".env"
        self.env_example = self.config_dir / ".env.example"
        
    def run_setup(self):
        """Run the complete setup process."""
        print("🚀 Enhanced Job Search Assistant Setup")
        print("=" * 50)
        
        # Step 1: Check environment file
        if not self.env_file.exists():
            print("\n📝 Creating environment configuration file...")
            self._create_env_file()
        
        # Step 2: Load current configuration
        env_vars = load_env_file(str(self.env_file))
        
        # Step 3: Configure API keys
        print("\n🔑 API Key Configuration")
        env_vars = self._configure_api_keys(env_vars)
        
        # Step 4: Test configuration
        print("\n🧪 Testing Search Configuration")
        self._test_search_setup(env_vars)
        
        # Step 5: Save configuration
        self._save_env_file(env_vars)
        
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the backend server: python backend/api/server.py")
        print("2. Run the frontend: npm run dev (in your Next.js directory)")
        print("3. Test the enhanced search in your web interface")
        
    def _create_env_file(self):
        """Create .env file from example."""
        if self.env_example.exists():
            # Copy example file
            with open(self.env_example, 'r') as src:
                content = src.read()
            with open(self.env_file, 'w') as dst:
                dst.write(content)
            print(f"✅ Created {self.env_file}")
        else:
            # Create basic .env file
            basic_content = """# Environment Configuration for Job Search Assistant
OPENAI_API_KEY=
GOOGLE_API_KEY=
CUSTOM_SEARCH_ENGINE_ID=
BING_API_KEY=
DATABASE_PATH=data/job_history.db
DAILY_RUN_HOUR=9
DAILY_RUN_MINUTE=0
DASHBOARD_HOST=localhost
DASHBOARD_PORT=8501
FLASK_ENV=development
PORT=5000
"""
            with open(self.env_file, 'w') as f:
                f.write(basic_content)
            print(f"✅ Created basic {self.env_file}")
    
    def _configure_api_keys(self, env_vars: Dict[str, str]) -> Dict[str, str]:
        """Interactive API key configuration."""
        
        # OpenAI API Key (Required)
        print("\n🔸 OpenAI API Key (Required)")
        current_openai = env_vars.get('OPENAI_API_KEY', '')
        if current_openai and current_openai.startswith('sk-'):
            print(f"Current: {current_openai[:10]}...{current_openai[-4:]}")
            if input("Keep current OpenAI API key? (y/n): ").lower() != 'y':
                env_vars['OPENAI_API_KEY'] = input("Enter new OpenAI API key: ").strip()
        else:
            print("OpenAI API key is required for the job search functionality.")
            print("Get your API key from: https://platform.openai.com/api-keys")
            env_vars['OPENAI_API_KEY'] = input("Enter OpenAI API key: ").strip()
        
        # Google Search API (Optional)
        print("\n🔸 Google Custom Search API (Optional - for enhanced web search)")
        print("This enables real-time web search with Google's Custom Search Engine.")
        print("Setup guide: https://developers.google.com/custom-search/v1/overview")
        
        if input("Configure Google Search API? (y/n): ").lower() == 'y':
            env_vars['GOOGLE_API_KEY'] = input("Enter Google API key: ").strip()
            env_vars['CUSTOM_SEARCH_ENGINE_ID'] = input("Enter Custom Search Engine ID: ").strip()
        
        # Bing Search API (Optional)
        print("\n🔸 Bing Search API (Optional - alternative to Google)")
        print("This provides an alternative web search option.")
        print("Setup guide: https://docs.microsoft.com/en-us/bing/search-apis/")
        
        if input("Configure Bing Search API? (y/n): ").lower() == 'y':
            env_vars['BING_API_KEY'] = input("Enter Bing API key: ").strip()
        
        return env_vars
    
    def _test_search_setup(self, env_vars: Dict[str, str]):
        """Test the search configuration."""
        openai_key = env_vars.get('OPENAI_API_KEY', '')
        google_key = env_vars.get('GOOGLE_API_KEY', '')
        bing_key = env_vars.get('BING_API_KEY', '')
        cse_id = env_vars.get('CUSTOM_SEARCH_ENGINE_ID', '')
        
        if not openai_key:
            print("❌ Cannot test without OpenAI API key")
            return
        
        try:
            print("🧪 Testing search engine configuration...")
            
            # Initialize enhanced search engine
            engine = EnhancedJobSearchEngine(
                openai_api_key=openai_key,
                google_api_key=google_key if google_key else None,
                bing_api_key=bing_key if bing_key else None,
                custom_search_engine_id=cse_id if cse_id else None
            )
            
            # Get capabilities
            capabilities = engine.get_search_capabilities()
            
            print("\n📊 Search Capabilities:")
            web_stats = capabilities.get('web_search_engine', {})
            providers = web_stats.get('providers_available', {})
            
            print(f"  ✅ OpenAI: {'Enabled' if web_stats.get('openai_enabled') else 'Disabled'}")
            print(f"  {'✅' if providers.get('google') else '❌'} Google Search: {'Enabled' if providers.get('google') else 'Disabled'}")
            print(f"  {'✅' if providers.get('bing') else '❌'} Bing Search: {'Enabled' if providers.get('bing') else 'Disabled'}")
            print(f"  ✅ DuckDuckGo: {'Always available (fallback)' if providers.get('duckduckgo') else 'Disabled'}")
            print(f"  📝 Job Sites Monitored: {web_stats.get('job_sites_monitored', 0)}")
            
            # Test search with a sample company
            test_company = "Microsoft"
            print(f"\n🔍 Testing search with '{test_company}'...")
            
            search_results = engine.search_company_jobs(test_company)
            job_listings = engine.extract_structured_jobs(search_results, test_company)
            
            print(f"  📄 Raw search results: {len(search_results)} characters")
            print(f"  💼 Structured jobs found: {len(job_listings)}")
            
            if job_listings:
                print("  ✅ Search test successful!")
                print(f"  📋 Sample job: {job_listings[0].get('job_title', 'N/A')}")
            else:
                print("  ⚠️  Search test completed but no jobs extracted")
                print("     This might be normal depending on current job postings")
            
        except Exception as e:
            print(f"❌ Search test failed: {e}")
            print("   Check your API keys and internet connection")
    
    def _save_env_file(self, env_vars: Dict[str, str]):
        """Save environment variables to .env file."""
        try:
            lines = []
            for key, value in env_vars.items():
                lines.append(f"{key}={value}")
            
            with open(self.env_file, 'w') as f:
                f.write('\n'.join(lines) + '\n')
            
            print(f"✅ Configuration saved to {self.env_file}")
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def test_server_connection(self, port: int = 5000):
        """Test if the Flask server is running."""
        try:
            response = requests.get(f"http://localhost:{port}/api/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Server is running on port {port}")
                return True
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return False
        except requests.exceptions.RequestException:
            print(f"❌ Server is not running on port {port}")
            return False


def main():
    """Main setup function."""
    setup_manager = EnhancedSetupManager()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test-server':
        # Test server connection
        setup_manager.test_server_connection()
    else:
        # Run full setup
        setup_manager.run_setup()


if __name__ == "__main__":
    main()
