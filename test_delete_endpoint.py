#!/usr/bin/env python3
"""
Test script to directly test the delete endpoint
"""

import requests
import json
from pathlib import Path

def test_delete_endpoint():
    """Test the delete endpoint directly"""
    
    # First, let's see what jobs exist
    jobs_file = Path("jobs.json")
    if jobs_file.exists():
        jobs = json.loads(jobs_file.read_text())
        print(f"Current jobs: {len(jobs)}")
        for i, job in enumerate(jobs):
            print(f"  {i}: {job['generator']}")
    
    # Test deleting the first job (index 0)
    if jobs:
        print(f"\nTesting delete of job 0: {jobs[0]['generator']}")
        
        # Simulate the POST request
        try:
            response = requests.post('http://localhost:5000/delete/0', timeout=5)
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to Flask app. Make sure it's running on localhost:5000")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("No jobs to delete")

if __name__ == "__main__":
    test_delete_endpoint() 