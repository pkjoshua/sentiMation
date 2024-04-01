import requests
import json
import logging
import os
import base64
from datetime import datetime
from PIL import Image

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Read settings and input image from the JSON file and input folder
input_dir = 'assets/inputs'
with open(os.path.join(input_dir, 'settings.json'), 'r') as file:
    settings = json.load(file)

user_integer = int(settings['user_integer'])
user_prompt = settings['user_prompt']
user_negative_prompt = settings['user_negative_prompt']

# Read and encode the input image
input_image_path = os.path.join(input_dir, 'input_image.JPG')  # Assuming the image is named 'input_image.png'
controlnet_image = encode_image_to_base64(input_image_path) if os.path.exists(input_image_path) else None

if controlnet_image is None:
    logging.error("Input image for ControlNet not found or could not be encoded.")
    exit(1)  # Exit if no input image is found

# Function to create and save the image from API response
def save_image_from_response(image_data, output_dir, image_index):
    image_bytes = base64.b64decode(image_data)
    file_path = os.path.join(output_dir, f'init_image_{image_index:04}.png')
    with open(file_path, "wb") as image_file:
        image_file.write(image_bytes)
    logging.info(f"Image saved: {file_path}")

# API and JSON Payload configuration
api_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

# Directory to save generated images
output_dir = 'assets/init'
os.makedirs(output_dir, exist_ok=True)

# Modified control_net_args configuration
control_net_args = {
    "input_image": controlnet_image,
    "resize_mode": "Crop and Resize",
    "module": "lineart_standard",
    "model": "control_v11p_sd15_lineart_fp16 [5c23b17d]",
    "weight": 1.0,
    "pixel_perfect": True,
    "control_mode": "ControlNet is more important"
}

# Generate and save images based on user_integer
for i in range(user_integer):
    # Define the JSON payload
    json_payload = {
        "prompt": user_prompt,
        "negative_prompt": user_negative_prompt,
        "batch_size": 1,
        "seed": -1,
        "sampler_name": "DPM++ 2M Karras",
        "steps": 25,
        "cfg_scale": 10,
        "width": 360,
        "height": 640,
        "alwayson_scripts": {
            "ControlNet": {"args": [control_net_args]}
        }
    }

    response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=json_payload)

    # Processing the response
    if response.status_code == 200:
        response_json = response.json()
        base64_image = response_json['images'][0]
        save_image_from_response(base64_image, output_dir, i)
    else:
        logging.error(f"API call failed. Status Code: {response.status_code}, Response: {response.text}")
        break  # Exit the loop if API call fails
