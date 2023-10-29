import requests
import base64
import json
import random
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='shrek_prompts.log', level=logging.INFO)

# Function to generate Shrek-related prompt
def generate_shrek_prompt():
    prompts = [
        "Shrek fighting a dragon on a volcano, radiant greatsword",
        "Shrek dueling a medieval knight, dark fantasy, dark souls, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.3>",
        "Shrek driving a futuristic motorcycle through the city, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.3>",
        "Shrek evading an apocalyptic robot, cinematic, <lora:shrek:0.3>",
        "Shrek and Donkey Kong on a magical quest, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.3>",
        "Shrek as a king of an alien planet, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.3>",
        "Shrek riding a futuristic motorcycle, tron, cyber, blue, virtual world, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.3>"
    ]
    chosen_prompt = random.choice(prompts)
    logging.info(f"{datetime.now()} - Chosen prompt: {chosen_prompt}")
    return chosen_prompt

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

# Define the payload for animate_diff_args
animate_diff_args = {
    "model": "mm_sd_v15_v2.ckpt",
    "format": ["GIF","PNG"],
    "enable": True,
    "video_length": 100,
    "fps": 20,
    "loop_number": 0,
    "closed_loop": "R+P",
    "batch_size": 16,
    "stride": 1,
    "overlap": -1,
    "interp": "Off",
    "interp_x": 10,
    "latent_power": 1,
    "latent_scale": 32,
    "last_frame": None,
    "latent_power_last": 1,
    "latent_scale_last": 32
}

# Define the JSON payload
json_payload = {
    "prompt": generate_shrek_prompt(),
    "negative_prompt": "bad quality, deformed, boring",
    "batch_size": 1,
    "sampler_name": "DPM++ 2M SDE Karras",
    "steps": 30,
    "cfg_scale": 10,
    "width": 512,
    "height": 512,
    "alwayson_scripts": {
        "AnimateDiff": {"args": [animate_diff_args]}
    }
}

# Define headers
headers = {
    "Content-Type": "application/json"
}

# Call the API
response = requests.post(api_url, headers=headers, json=json_payload)

# Debugging
print("Full API Response:", response.json())
print("HTTP Status Code:", response.status_code)

# Parse the JSON response
response_json = response.json()
