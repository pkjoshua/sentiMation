#!/usr/bin/env python3
"""
Comprehensive API Connection Test Script
Tests various ways to connect to Automatic1111 API from container
"""
import os
import sys
import requests
import socket
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection(host, port, endpoint="/sdapi/v1/txt2img"):
    """Test connection to a specific host and port"""
    url = f"http://{host}:{port}{endpoint}"
    print(f"\n🔍 Testing: {url}")
    
    try:
        # Test basic connectivity first
        print(f"  📡 Testing basic connectivity...")
        response = requests.get(f"http://{host}:{port}", timeout=5)
        print(f"  ✅ Basic connectivity: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Basic connectivity failed: {e}")
        return False
    
    try:
        # Test the actual API endpoint
        print(f"  🎯 Testing API endpoint...")
        response = requests.post(url, json={}, timeout=10)
        print(f"  ✅ API endpoint: {response.status_code}")
        if response.status_code == 400:
            print(f"  📝 Response: {response.text[:200]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ❌ API endpoint failed: {e}")
        return False

def get_network_info():
    """Get network information for debugging"""
    print("\n🌐 Network Information:")
    
    # Get container's network info
    try:
        container_ip = subprocess.check_output(['hostname', '-i']).decode().strip()
        print(f"  📦 Container IP: {container_ip}")
    except:
        print(f"  📦 Container IP: Could not determine")
    
    # Get hostname
    try:
        hostname = subprocess.check_output(['hostname']).decode().strip()
        print(f"  🏷️  Hostname: {hostname}")
    except:
        print(f"  🏷️  Hostname: Could not determine")
    
    # Test DNS resolution
    hosts_to_test = [
        'host.docker.internal',
        'localhost',
        '127.0.0.1',
        '172.17.0.1',  # Docker bridge network gateway
        'host.gateway',  # Docker host gateway
    ]
    
    print(f"  🔍 DNS Resolution Tests:")
    for host in hosts_to_test:
        try:
            ip = socket.gethostbyname(host)
            print(f"    {host} -> {ip}")
        except socket.gaierror:
            print(f"    {host} -> Failed to resolve")

def test_all_possible_hosts():
    """Test all possible ways to reach the host"""
    print("\n🚀 Testing All Possible Host Configurations:")
    
    # Get environment variables
    sd_host = os.environ.get('SD_HOST', '127.0.0.1')
    sd_port = os.environ.get('SD_PORT', '7860')
    
    print(f"  📋 Current .env settings:")
    print(f"    SD_HOST: {sd_host}")
    print(f"    SD_PORT: {sd_port}")
    
    # Test the configured host
    print(f"\n🎯 Testing configured host...")
    test_connection(sd_host, sd_port)
    
    # Test common Docker host addresses
    docker_hosts = [
        'host.docker.internal',
        '172.17.0.1',  # Docker bridge gateway
        'host.gateway',
        'localhost',
        '127.0.0.1',
    ]
    
    print(f"\n🔍 Testing common Docker host addresses:")
    for host in docker_hosts:
        test_connection(host, sd_port)
    
    # Try to get WSL2 host IP if we're in WSL2
    try:
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if line.startswith('nameserver'):
                    wsl2_host = line.split()[1]
                    print(f"\n🪟 Testing WSL2 host IP: {wsl2_host}")
                    test_connection(wsl2_host, sd_port)
                    break
    except:
        print(f"\n🪟 WSL2 host IP: Could not determine")

def test_automatic1111_status():
    """Test if Automatic1111 is running and accessible"""
    print("\n🤖 Testing Automatic1111 Status:")
    
    # Test common Automatic1111 endpoints
    endpoints = [
        '/sdapi/v1/txt2img',
        '/sdapi/v1/img2img',
        '/sdapi/v1/progress',
        '/sdapi/v1/samplers',
    ]
    
    hosts_to_test = [
        'host.docker.internal',
        '172.17.0.1',
        'localhost',
    ]
    
    for host in hosts_to_test:
        print(f"\n🎯 Testing {host}:")
        for endpoint in endpoints:
            try:
                url = f"http://{host}:7860{endpoint}"
                response = requests.get(url, timeout=5)
                print(f"  ✅ {endpoint}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"  ❌ {endpoint}: {str(e)[:50]}...")

def suggest_solutions():
    """Suggest solutions based on test results"""
    print("\n💡 Troubleshooting Suggestions:")
    print("  1. 🔧 Check if Automatic1111 is running on the host")
    print("  2. 🌐 Ensure Automatic1111 is bound to 0.0.0.0, not just 127.0.0.1")
    print("  3. 🔥 Check firewall settings on the host")
    print("  4. 🐳 Try different SD_HOST values in .env:")
    print("     - host.docker.internal (Docker Desktop)")
    print("     - 172.17.0.1 (Docker bridge)")
    print("     - <your-host-ip> (LAN IP)")
    print("  5. 🔄 Restart Automatic1111 with --listen flag")
    print("  6. 📡 Check if port 7860 is open on the host")

if __name__ == "__main__":
    print("🔧 Automatic1111 API Connection Diagnostic Tool")
    print("=" * 50)
    
    # Get network information
    get_network_info()
    
    # Test all possible hosts
    test_all_possible_hosts()
    
    # Test Automatic1111 status
    test_automatic1111_status()
    
    # Provide suggestions
    suggest_solutions()
    
    print("\n✅ Diagnostic complete!") 