#!/usr/bin/env python3
"""
Test script to verify SD API configuration
"""
import os
import sys
from pathlib import Path

# Add the generators directory to the path
sys.path.append(str(Path(__file__).parent / "generators"))

# Import the config
from sd_api_config import get_api_url, SD_HOST, SD_PORT, SD_BASE_URL

print("=== SD API Configuration Test ===")
print(f"SD_HOST: {SD_HOST}")
print(f"SD_PORT: {SD_PORT}")
print(f"SD_BASE_URL: {SD_BASE_URL}")
print(f"txt2img URL: {get_api_url('txt2img')}")
print(f"img2img URL: {get_api_url('img2img')}")

# Test environment variables
print("\n=== Environment Variables ===")
for key in ['SD_HOST', 'SD_PORT', 'SD_BASE_URL', 'SD_TXT2IMG_URL', 'SD_IMG2IMG_URL']:
    value = os.environ.get(key, 'NOT SET')
    print(f"{key}: {value}")

print("\n=== Configuration Complete ===") 