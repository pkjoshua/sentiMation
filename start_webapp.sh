#!/bin/bash

# SentiMation Web Application Startup Script

echo "Starting SentiMation Web Application..."

# Check if we're in the right directory
if [ ! -f "webapp/app.py" ]; then
    echo "Error: webapp/app.py not found. Please run this script from the SentiMation root directory."
    exit 1
fi

# Create necessary directories
mkdir -p webapp/static/generated

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing Flask..."
    pip install flask
fi

# Start the web application
echo "Starting Flask application on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

cd webapp
python app.py 