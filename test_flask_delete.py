#!/usr/bin/env python3
"""
Test Flask delete route directly
"""

import sys
import os
sys.path.append('webapp')

# Import Flask app
from app import app

def test_delete_route():
    """Test the delete route directly"""
    
    with app.test_client() as client:
        print("🧪 Testing Flask Delete Route")
        print("=" * 30)
        
        # Test the test-delete route first
        response = client.post('/test-delete/0')
        print(f"Test delete response: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        
        # Now test the actual delete route
        response = client.post('/delete/0')
        print(f"Actual delete response: {response.status_code}")
        
        # Check if we got redirected
        if response.status_code == 302:
            print("✅ Got redirect (expected)")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")

if __name__ == "__main__":
    test_delete_route() 