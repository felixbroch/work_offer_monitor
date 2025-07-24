#!/usr/bin/env python3
"""
Test script for OpenAI Job Search Agent

This script tests the new OpenAI-based job search functionality.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from src.core.advanced_job_agent import OpenAIJobSearchAgent, search_jobs_with_openai_agent
from config.config import OPENAI_SETTINGS

def test_basic_agent():
    """Test the basic OpenAI agent functionality."""
    print("🧪 Testing OpenAI Job Search Agent")
    print("=" * 50)
    
    try:
        # Initialize agent
        agent = OpenAIJobSearchAgent()
        print("✅ Agent initialized successfully")
        
        # Test with a well-known company
        print("\n🔍 Testing job search for OpenAI...")
        jobs = agent.search_company_jobs("OpenAI", "https://openai.com/careers/")
        
        print(f"📊 Found {len(jobs)} jobs")
        
        if jobs:
            print("\n📋 Job Results:")
            for i, job in enumerate(jobs[:3], 1):  # Show first 3 jobs
                print(f"\n{i}. {job.get('title', 'Unknown Title')}")
                print(f"   Location: {job.get('location', 'Unknown')}")
                print(f"   Relevance: {job.get('relevance_score', 0)}%")
                print(f"   URL: {job.get('url', 'N/A')}")
                if job.get('reasoning'):
                    print(f"   Reasoning: {job.get('reasoning')}")
        else:
            print("❌ No jobs found")
            
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        import traceback
        traceback.print_exc()

def test_integration():
    """Test the integration function."""
    print("\n🔧 Testing Integration Function")
    print("=" * 50)
    
    try:
        # Test companies
        test_companies = [
            {"company_name": "Microsoft", "career_page_url": "https://careers.microsoft.com/"},
            {"company_name": "Google", "career_page_url": "https://careers.google.com/"}
        ]
        
        api_key = OPENAI_SETTINGS.get("api_key")
        if not api_key or api_key == "your_openai_api_key_here":
            print("❌ No valid API key found. Please set OPENAI_API_KEY in .env file")
            return
            
        print("🔍 Searching jobs across multiple companies...")
        jobs = search_jobs_with_openai_agent(test_companies, api_key)
        
        print(f"📊 Total jobs found: {len(jobs)}")
        
        if jobs:
            # Group by company
            by_company = {}
            for job in jobs:
                company = job.get('company_name', 'Unknown')
                if company not in by_company:
                    by_company[company] = []
                by_company[company].append(job)
            
            print("\n📈 Results by Company:")
            for company, company_jobs in by_company.items():
                print(f"  {company}: {len(company_jobs)} jobs")
                
        else:
            print("❌ No jobs found across all companies")
            
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("🚀 OpenAI Job Search Agent Test Suite")
    print("=" * 60)
    
    # Check API key first
    api_key = OPENAI_SETTINGS.get("api_key")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ ERROR: OpenAI API key not configured!")
        print("Please set OPENAI_API_KEY in your .env file")
        print("Get your API key from: https://platform.openai.com/api-keys")
        return
    
    print(f"✅ API key found: {api_key[:20]}...")
    
    # Run tests
    test_basic_agent()
    test_integration()
    
    print("\n🎯 Test Suite Completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
