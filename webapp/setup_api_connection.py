#!/usr/bin/env python3
"""
Setup script for Stable Diffusion API connection
"""
import os
import subprocess
import sys

def print_instructions():
    """Print setup instructions"""
    print("🚀 SentiMation API Connection Setup")
    print("=" * 50)
    print()
    print("📋 STEP-BY-STEP INSTRUCTIONS:")
    print()
    print("1️⃣  START STABLE DIFFUSION ON WINDOWS:")
    print("   cd path/to/stable-diffusion-webui")
    print("   python launch.py --api --listen --port 7860")
    print()
    print("2️⃣  VERIFY STABLE DIFFUSION IS RUNNING:")
    print("   Open browser: http://localhost:7860")
    print("   You should see the Stable Diffusion WebUI")
    print()
    print("3️⃣  FIND YOUR WINDOWS IP ADDRESS:")
    print("   On Windows, run: ipconfig")
    print("   Look for 'IPv4 Address' under your main network adapter")
    print("   Example: 192.168.1.100")
    print()
    print("4️⃣  UPDATE CONFIGURATION:")
    print("   Edit webapp/config.py and update SD_API_URL_DIRECT")
    print("   Or set environment variable:")
    print("   export SD_API_URL='http://YOUR_WINDOWS_IP:7860/sdapi/v1/img2img'")
    print()
    print("5️⃣  TEST CONNECTION:")
    print("   python test_all_connections.py")
    print()

def test_current_config():
    """Test the current configuration"""
    print("🧪 Testing current configuration...")
    try:
        from config import SD_API_URL
        print(f"Current API URL: {SD_API_URL}")
        
        # Test the connection
        import requests
        test_url = SD_API_URL.replace('/sdapi/v1/img2img', '/sdapi/v1/progress')
        response = requests.get(test_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Connection successful!")
            return True
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_current_config()
    else:
        print_instructions()
        
        # Ask if user wants to test
        response = input("\nWould you like to test the current configuration? (y/n): ")
        if response.lower() in ['y', 'yes']:
            test_current_config()

if __name__ == "__main__":
    main() 