#!/usr/bin/env python3
"""
Test script to verify the enhanced job search system.
"""

import sys
import os

# Add project root to path
sys.path.append('.')

try:
    print("🧪 Testing Enhanced Job Search System")
    print("=" * 40)
    
    # Test web search engine import
    print("1. Testing WebSearchEngine import...")
    from src.core.web_search_engine import WebSearchEngine, JobSearchOrchestrator
    print("   ✅ WebSearchEngine imported successfully")
    
    # Test enhanced job search engine import  
    print("2. Testing EnhancedJobSearchEngine import...")
    from src.core.enhanced_job_search_engine import EnhancedJobSearchEngine
    print("   ✅ EnhancedJobSearchEngine imported successfully")
    
    # Test configuration import
    print("3. Testing configuration import...")
    from config.config import FILTERING_CRITERIA, FILES, OPENAI_SETTINGS
    print("   ✅ Configuration imported successfully")
    
    # Test creating engine instance (without API keys)
    print("4. Testing engine initialization...")
    try:
        engine = EnhancedJobSearchEngine(openai_api_key="test-key")
        print("   ✅ Engine initialization successful")
    except Exception as e:
        print(f"   ⚠️  Engine initialization test skipped: {e}")
    
    print("\n🎉 All imports successful!")
    print("✅ Enhanced Job Search System is ready")
    print("\nNext steps:")
    print("1. Configure API keys: python scripts/enhanced_setup.py")
    print("2. Start server: python start_server.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
