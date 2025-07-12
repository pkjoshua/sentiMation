#!/usr/bin/env python3
"""
Test the main page delete functionality
"""

import requests
import json
from pathlib import Path

def test_main_page_delete():
    """Test the main page delete functionality"""
    
    print("🏠 Testing Main Page Delete Functionality")
    print("=" * 40)
    
    # First, check current jobs
    try:
        response = requests.get('http://localhost:5001/debug-jobs', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current jobs count: {data['jobs_count']}")
            if data['jobs']:
                print("Current jobs:")
                for i, job in enumerate(data['jobs']):
                    print(f"  {i}: {job['generator']}")
        else:
            print("❌ Could not get current jobs")
            return
    except Exception as e:
        print(f"❌ Error getting jobs: {e}")
        return
    
    # Test the main page loads
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        print(f"✅ Main page loads: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading main page: {e}")
        return
    
    print("\n🎯 Now test the delete functionality:")
    print("1. Go to: http://localhost:5001")
    print("2. Click the delete button on any job")
    print("3. Confirm the deletion")
    print("4. The job should be removed immediately")
    
    print("\n🔍 If it still doesn't work:")
    print("- Open browser developer tools (F12)")
    print("- Check the Console tab for any errors")
    print("- Check the Network tab to see if the form submits")

if __name__ == "__main__":
    test_main_page_delete() 