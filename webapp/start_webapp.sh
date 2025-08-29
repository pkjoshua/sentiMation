#!/bin/bash

# SentiMation WebApp Startup Script

echo "Starting SentiMation WebApp..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found. Please run this script from the webapp directory."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Create necessary directories
mkdir -p webapp/static/generated

# Start the application
echo "Starting Flask application..."
echo "Access the webapp at: http://localhost:5000"
echo "Press Ctrl+C to stop"

python3 app.py
