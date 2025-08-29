#!/usr/bin/env python3
"""
Configuration for SentiMation webapp
"""
import os

# Stable Diffusion API configuration
# Try these options in order of preference:

# Option 1: WSL2 host (most common)
SD_API_URL_WSL2 = "http://host.docker.internal:7860/sdapi/v1/img2img"

# Option 2: Windows host IP (if host.docker.internal doesn't work)
# To find your Windows IP, run 'ipconfig' on Windows and look for your main network adapter
SD_API_URL_WINDOWS_IP = "http://172.17.0.1:7860/sdapi/v1/img2img"

# Option 3: WSL2 gateway
SD_API_URL_WSL2_GATEWAY = "http://172.18.0.1:7860/sdapi/v1/img2img"

# Option 4: Direct Windows IP (REPLACE WITH YOUR ACTUAL WINDOWS IP)
# Run 'ipconfig' on Windows to find your IP address
SD_API_URL_DIRECT = "http://192.168.1.100:7860/sdapi/v1/img2img"  # Replace with your Windows IP

# Get from environment variable or use default
SD_API_URL = os.getenv('SD_API_URL', SD_API_URL_WSL2)

# Base for health checks and general SD API
AUTO1111_BASE_URL = os.getenv('AUTO1111_BASE_URL', 'http://host.docker.internal:7860')

# Host Service Configuration
# Windows host service that handles job scheduling and execution
HOST_SERVICE_URL = os.getenv('HOST_SERVICE_URL', 'http://host.docker.internal:7070')

# Webapp public URL (how Windows host calls back into this app)
# Default assumes port 5000 is published on localhost
WEBAPP_PUBLIC_URL = os.getenv('WEBAPP_PUBLIC_URL', 'http://localhost:5000')

# Shared secret for host callback authentication
HOST_CALLBACK_TOKEN = os.getenv('HOST_CALLBACK_TOKEN', 'dev-callback-token-change-me')

# Health check interval seconds
HEALTHCHECK_INTERVAL_SEC = int(os.getenv('HEALTHCHECK_INTERVAL_SEC', '15'))

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'webapp.log')

# Web app configuration
WEBAPP_HOST = os.getenv('WEBAPP_HOST', '0.0.0.0')
WEBAPP_PORT = int(os.getenv('WEBAPP_PORT', '5000'))

# Instructions for setup:
# 1. Start Stable Diffusion on Windows: python launch.py --api --listen --port 7860
# 2. Find your Windows IP: ipconfig (look for IPv4 address)
# 3. Update SD_API_URL_DIRECT above with your Windows IP
# 4. Or set environment variable: export SD_API_URL="http://YOUR_WINDOWS_IP:7860/sdapi/v1/img2img"
# 5. Start the host service on Windows: Run scripts/win/host_service.ps1 as Administrator 