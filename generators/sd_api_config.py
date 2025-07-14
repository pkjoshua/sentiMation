import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Get SD API configuration from environment variables
SD_HOST = os.environ.get('SD_HOST', '127.0.0.1')
SD_PORT = os.environ.get('SD_PORT', '7860')
SD_BASE_URL = os.environ.get('SD_BASE_URL', f"http://{SD_HOST}:{SD_PORT}")

# API endpoints
SD_TXT2IMG_URL = os.environ.get('SD_TXT2IMG_URL', f"{SD_BASE_URL}/sdapi/v1/txt2img")
SD_IMG2IMG_URL = os.environ.get('SD_IMG2IMG_URL', f"{SD_BASE_URL}/sdapi/v1/img2img")

def get_api_url(endpoint_type='txt2img'):
    """Get the appropriate API URL based on endpoint type"""
    if endpoint_type == 'txt2img':
        return SD_TXT2IMG_URL
    elif endpoint_type == 'img2img':
        return SD_IMG2IMG_URL
    else:
        raise ValueError(f"Unknown endpoint type: {endpoint_type}")

# For backward compatibility
api_url = SD_TXT2IMG_URL  # Default to txt2img 