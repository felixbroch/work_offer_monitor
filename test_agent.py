#!/usr/bin/env python3
"""
Test Advanced Job Search Agent

This script demonstrates the new OpenAI agent-based job search system.
"""

import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.advanced_job_agent import AdvancedJobSearchAgent
from config.config import OPENAI_SETTINGS

def test_agent():
    """Test the advanced job search agent."""
    print("🧪 Testing Advanced Job Search Agent")
    print("=" * 50)
    
    # Check API key
    api_key = OPENAI_SETTINGS.get("api_key")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Error: OpenAI API key not configured.")
        print("Please set your API key in the config or environment.")
        return
    
    print(f"✅ API key configured")
    
    # Initialize agent
    try:
        agent = AdvancedJobSearchAgent(api_key)
        print(f"✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return
    
    # Test companies
    test_companies = [
        {"company_name": "OpenAI", "career_page_url": "https://openai.com/careers/"},
        {"company_name": "Microsoft", "career_page_url": "https://careers.microsoft.com/"},
    ]
    
    print(f"\n🎯 Testing with {len(test_companies)} companies...")
    
    for i, company in enumerate(test_companies, 1):
        company_name = company["company_name"]
        career_url = company["career_page_url"]
        
        print(f"\n--- Testing {company_name} ({i}/{len(test_companies)}) ---")
        
        try:
            jobs = agent.search_company_jobs(company_name, career_url)
            
            if jobs:
                print(f"✅ Found {len(jobs)} relevant jobs!")
                for job in jobs:
                    print(f"  • {job.get('title', 'Unknown Title')}")
                    print(f"    Location: {job.get('location', 'Unknown')}")
                    print(f"    Relevance: {job.get('relevance_score', 0)}%")
                    print(f"    Reasoning: {job.get('analysis_reasoning', 'No reasoning')[:100]}...")
                    print()
            else:
                print(f"❌ No relevant jobs found for {company_name}")
                
        except Exception as e:
            print(f"❌ Error testing {company_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    test_agent()
