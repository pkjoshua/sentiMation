#!/usr/bin/env python3
"""
Test the web interface functionality
"""

import requests
import json
from pathlib import Path

def test_web_interface():
    """Test the web interface"""
    
    print("🌐 Testing Web Interface")
    print("=" * 30)
    
    # Test the main page
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        print(f"Main page status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print("❌ Main page failed to load")
    except Exception as e:
        print(f"❌ Error accessing main page: {e}")
    
    # Test the debug jobs endpoint
    try:
        response = requests.get('http://localhost:5001/debug-jobs', timeout=5)
        print(f"Debug jobs status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug jobs endpoint works. Jobs count: {data['jobs_count']}")
        else:
            print("❌ Debug jobs endpoint failed")
    except Exception as e:
        print(f"❌ Error accessing debug jobs: {e}")
    
    # Test the test form
    try:
        response = requests.get('http://localhost:5001/test-form', timeout=5)
        print(f"Test form status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Test form loads successfully")
        else:
            print("❌ Test form failed to load")
    except Exception as e:
        print(f"❌ Error accessing test form: {e}")

if __name__ == "__main__":
    test_web_interface() 