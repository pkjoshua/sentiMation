import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Automatic1111 API Configuration
SD_HOST = os.environ.get('SD_HOST', '127.0.0.1')
SD_PORT = os.environ.get('SD_PORT', '7860')
SD_BASE_URL = f"http://{SD_HOST}:{SD_PORT}"

# API endpoints
SD_TXT2IMG_URL = f"{SD_BASE_URL}/sdapi/v1/txt2img"
SD_IMG2IMG_URL = f"{SD_BASE_URL}/sdapi/v1/img2img"

# Environment variables that will be passed to generator scripts
SD_ENV_VARS = {
    'SD_HOST': SD_HOST,
    'SD_PORT': SD_PORT,
    'SD_BASE_URL': SD_BASE_URL,
    'SD_TXT2IMG_URL': SD_TXT2IMG_URL,
    'SD_IMG2IMG_URL': SD_IMG2IMG_URL,
} 