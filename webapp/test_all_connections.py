#!/usr/bin/env python3
"""
Comprehensive test script to find the correct hostname for Windows host
"""
import requests
import subprocess
import json
import time

def get_windows_ip():
    """Try to get Windows host IP"""
    try:
        # Try to get the default gateway (usually Windows host)
        result = subprocess.run(['ip', 'route', 'show', 'default'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'default via' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]  # This should be the Windows host IP
    except Exception as e:
        print(f"Could not get Windows IP: {e}")
    return None

def test_connection(url, description):
    """Test connection to a specific URL"""
    print(f"\n🔍 Testing {description}: {url}")
    try:
        response = requests.get(url.replace('/sdapi/v1/img2img', '/sdapi/v1/progress'), 
                              timeout=5)
        if response.status_code == 200:
            print(f"✅ SUCCESS! {description} works!")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {description}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed: {description}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout: {description}")
        return False
    except Exception as e:
        print(f"❌ Error: {description} - {e}")
        return False

def main():
    """Test all possible connection options"""
    print("🚀 Testing Stable Diffusion API connections...")
    print("=" * 60)
    
    # Get Windows IP
    windows_ip = get_windows_ip()
    if windows_ip:
        print(f"📍 Detected Windows host IP: {windows_ip}")
    
    # Test different hostname options
    test_urls = [
        ("http://host.docker.internal:7860/sdapi/v1/img2img", "host.docker.internal (WSL2)"),
        ("http://172.17.0.1:7860/sdapi/v1/img2img", "172.17.0.1 (Docker bridge)"),
        ("http://172.18.0.1:7860/sdapi/v1/img2img", "172.18.0.1 (WSL2 gateway)"),
    ]
    
    # Add Windows IP if detected
    if windows_ip:
        test_urls.append((f"http://{windows_ip}:7860/sdapi/v1/img2img", f"{windows_ip} (Detected Windows IP)"))
    
    # Test each URL
    working_urls = []
    for url, description in test_urls:
        if test_connection(url, description):
            working_urls.append((url, description))
    
    # Summary
    print("\n" + "=" * 60)
    if working_urls:
        print("🎉 WORKING CONNECTIONS FOUND:")
        for url, description in working_urls:
            print(f"   ✅ {description}: {url}")
        
        print(f"\n💡 RECOMMENDED CONFIGURATION:")
        print(f"   Set environment variable: SD_API_URL={working_urls[0][0]}")
        print(f"   Or update config.py to use: {working_urls[0][0]}")
        
        # Test the first working URL more thoroughly
        print(f"\n🧪 Testing API endpoints with: {working_urls[0][0]}")
        base_url = working_urls[0][0].replace('/sdapi/v1/img2img', '')
        
        endpoints = ['/sdapi/v1/progress', '/sdapi/v1/options', '/sdapi/v1/sd-models']
        for endpoint in endpoints:
            try:
                response = requests.get(base_url + endpoint, timeout=5)
                print(f"   {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"   {endpoint}: ❌ {e}")
        
    else:
        print("❌ NO WORKING CONNECTIONS FOUND")
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("1. Make sure Stable Diffusion WebUI is running on Windows")
        print("2. Start with API enabled: python launch.py --api --listen --port 7860")
        print("3. Check Windows firewall settings")
        print("4. Try running: netstat -an | findstr 7860 (on Windows)")
        print("5. Consider using port forwarding or VPN")

if __name__ == "__main__":
    main() 