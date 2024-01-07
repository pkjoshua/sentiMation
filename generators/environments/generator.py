import requests
import base64
import json
import logging
import os

INITIAL_DENOISING_STRENGTH = 0.50
INITIAL_CFG_SCALE = 11
CONTINUING_DENOISING_STRENGTH = 0.50
CONTINUING_CFG_SCALE = 4
USE_CURRENT_FRAME = True 

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to read prompt
def read_prompt(file_path):
    with open(file_path, "r") as file:
        return file.readline().strip()

# Read prompt from file
prompt = read_prompt("chosen_prompt.txt")

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/img2img"

# Directories
frames_dir = "assets\\frames"
generation_dir = "assets\\lowscale"
os.makedirs(generation_dir, exist_ok=True)

frame_files = sorted(os.listdir(frames_dir))
previous_generation_base64 = None  # Variable to store the base64 of the previous generation

for index, frame_file in enumerate(frame_files):
    current_frame_base64 = encode_image_to_base64(os.path.join(frames_dir, frame_file))

    # Handling init_image based on settings
    if index == 0 or USE_CURRENT_FRAME:
        init_image = current_frame_base64
        denoising_strength = INITIAL_DENOISING_STRENGTH
        cfg_scale = INITIAL_CFG_SCALE
    else:
        init_image = current_frame_base64
        denoising_strength = CONTINUING_DENOISING_STRENGTH
        cfg_scale = CONTINUING_CFG_SCALE

    # Modified control_net_args configuration
    control_net_args = [{
        "input_image": previous_generation_base64 if previous_generation_base64 else "null",
        "resize_mode": "Just Resize",
        "module": "reference_adain+attn",
        "model": "none",
        "weight": 0.45,
        "pixel_perfect": True,
        "control_mode": "ControlNet is more important"
    }, {
        "input_image": previous_generation_base64 if previous_generation_base64 else "null",
        "resize_mode": "Just Resize",
        "module": "none",
        "model": "temporalnetv3 [b146ac48]",
        "weight": 0.2,
        "pixel_perfect": True,
        "control_mode": "Prompt is more important"
    }]

    # Define the JSON payload
    json_payload = {
        "init_images": [init_image],
        "denoising_strength": denoising_strength,
        "include_init_images": True,
        "prompt": prompt,
        "negative_prompt": "bad quality, deformed, boring, pixelated, blurry, unclear, artifact, nude, nsfw, humans, human hands",
        "batch_size": 1,
        "seed": 1337,
        "sampler_name": "DPM++ 2M Karras",
        "steps": 20,
        "cfg_scale": cfg_scale,
        "width": 360,
        "height": 640,
        "alwayson_scripts": {
            "ControlNet": {"args": control_net_args}
        }
    }

    # Call the API
    response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=json_payload)

    if response.status_code == 200:
        r = response.json()
        if 'images' in r and r['images']:
            base64_data = r['images'][0]
            image_data = base64.b64decode(base64_data)

            # Save the current generation and update the previous generation variable
            output_path = os.path.join(generation_dir, f"generation_{index:04d}.jpg")
            with open(output_path, 'wb') as file:
                file.write(image_data)
            previous_generation_base64 = base64_data
        else:
            logging.error(f"No image data found in the response for frame: {frame_file}")
    else:
        logging.error(f"API call failed for frame: {frame_file}. Status Code: {response.status_code}, Response: {response.text}")
