#!/usr/bin/env python3
"""
Test script to verify Stable Diffusion API connection
"""
import requests
import json
import os

# Get API URL from environment or use default
SD_API_URL = os.getenv('SD_API_URL', "http://host.docker.internal:7860/sdapi/v1/img2img")
SD_BASE_URL = SD_API_URL.replace('/sdapi/v1/img2img', '')

def test_api_connection():
    """Test the Stable Diffusion API connection"""
    print(f"Testing connection to: {SD_BASE_URL}")
    
    try:
        # Test basic connectivity
        response = requests.get(f"{SD_BASE_URL}/sdapi/v1/progress", timeout=5)
        print(f"✅ Progress endpoint: {response.status_code}")
        
        # Test options endpoint
        response = requests.get(f"{SD_BASE_URL}/sdapi/v1/options", timeout=5)
        print(f"✅ Options endpoint: {response.status_code}")
        
        # Test models endpoint
        response = requests.get(f"{SD_BASE_URL}/sdapi/v1/sd-models", timeout=5)
        print(f"✅ Models endpoint: {response.status_code}")
        
        print("\n🎉 API connection successful!")
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure Stable Diffusion WebUI is running on your Windows machine")
        print("2. Ensure it's started with the --api flag: python launch.py --api")
        print("3. Check that port 7860 is accessible")
        print("4. Try using a different hostname if host.docker.internal doesn't work")
        return False
        
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_api_connection() 