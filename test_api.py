#!/usr/bin/env python3
"""
Quick OpenAI API Test

Test if the OpenAI API key supports web search functionality.
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from config.config import OPENAI_SETTINGS
import openai

def test_openai_connection():
    """Test basic OpenAI API connection."""
    print("🧪 Testing OpenAI API Connection")
    print("=" * 40)
    
    api_key = OPENAI_SETTINGS.get("api_key")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ No API key found in config")
        return False
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Test basic chat completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello! Can you help me search for jobs?"}],
            max_tokens=50
        )
        
        print("✅ Basic API connection works")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_web_search_capability():
    """Test if web search tools are available."""
    print("\n🌐 Testing Web Search Capability")
    print("=" * 40)
    
    api_key = OPENAI_SETTINGS.get("api_key")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Try to use web search tool
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful assistant with web search capabilities."
                },
                {
                    "role": "user", 
                    "content": "Can you search for current job openings at OpenAI? Just tell me if you can access their careers page."
                }
            ],
            tools=[
                {
                    "type": "web_search",
                    "web_search": {
                        "description": "Search the web for information"
                    }
                }
            ],
            tool_choice="auto",
            max_tokens=200
        )
        
        message = response.choices[0].message
        
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print("✅ Web search tools available and used!")
            print("🎯 Ready for job search agent!")
        else:
            print("⚠️  Web search tools available but not used automatically")
            print("Response:", message.content)
        
        return True
        
    except Exception as e:
        print(f"❌ Web search test failed: {e}")
        
        # Try without web search to see if it's a model/tool issue
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            print("✅ GPT-4o model access works (web search may not be enabled)")
        except Exception as e2:
            print(f"❌ GPT-4o model access failed: {e2}")
            print("💡 Try using gpt-3.5-turbo for basic functionality")
        
        return False

def main():
    """Run all tests."""
    print("🚀 OpenAI API Test Suite")
    print("=" * 50)
    
    # Basic connection test
    if not test_openai_connection():
        print("\n❌ Basic API connection failed - check your API key")
        return
    
    # Web search capability test
    test_web_search_capability()
    
    print("\n🎯 Test Complete!")
    print("=" * 50)
    
    print("\nNext steps:")
    print("1. If web search works: Ready to use agent-based job search!")
    print("2. If web search fails: You can still use basic job search")
    print("3. Run: python main.py (choose option 2 for agent search)")

if __name__ == "__main__":
    main()
