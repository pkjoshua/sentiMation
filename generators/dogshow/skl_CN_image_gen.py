import requests
import json
import random
import logging
import os
import base64
import textwrap
from datetime import datetime
from PIL import Image

# Set up logging
logging.basicConfig(filename="skl_gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def generate_skl_prompt():
    prompts = [
        textwrap.dedent("""\
        Icy landscape, frozen tundra, glacial beauty, mesmerizing, 4k, high detail, smooth, sharp focus, hdr, high resolution """),

        textwrap.dedent("""\
        Lava flows, volcanic, fiery environment, intense, 4k, high resolution, illustration, epic, explosion, smooth, sharp focus, hdr, high resolution"""),

        textwrap.dedent("""\
        Cyberpunk cityscape, electric, neon lights, futuristic, vibrant, 4k, ultra high definition, smooth, sharp focus, hdr, high resolution"""),

        textwrap.dedent("""\
        Steampunk world, gears and steam, vintage technology, intricate, 4k, sharp details, smooth, sharp focus, hdr, high resolution"""),

        textwrap.dedent("""\
        Desert dunes, arid climate, sandstorm, vast, mesmerizing, 4k, high clarity, smooth, sharp focus, hdr, high resolution"""),

        textwrap.dedent("""\
        Beach paradise, tropical, sunny, ocean view, serene, beautiful, 4k, cinematic, smooth, sharp focus, hdr, high resolution"""),

        textwrap.dedent("""\
        psychedelic art in drdjns style of photorealistic marbles, intricate patterns, complex and detailed, masterpiece, 8k, hdr""")
    ]
    chosen_prompt = random.choice(prompts)
    logging.info(f"Full chosen prompt: {chosen_prompt}")

    # Splitting the chosen prompt and logging the first line
    first_line_prompt = chosen_prompt.splitlines()[0]
    logging.info(f"First line of chosen prompt for API payload: {first_line_prompt}")

    # Write the full prompt with transitions to a file
    with open("chosen_prompt.txt", "w") as f:
        f.write(chosen_prompt)

    return first_line_prompt

# Function to process the latest image from a directory
def process_latest_image(source_dir, used_dir):
    try:
        files = [file for file in os.listdir(source_dir) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not files:
            logging.error("No images found in the directory.")
            return None

        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(source_dir, f)))
        image_path = os.path.join(source_dir, latest_file)

        # Process and save the image in the used directory
        with Image.open(image_path) as img:
            # Assuming any image processing like resizing if required
            used_image_path = os.path.join(used_dir, os.path.basename(image_path))
            img.save(used_image_path)

        # Encode the image for use in the payload
        with open(used_image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Remove the original image
        os.remove(image_path)
        logging.info(f"Processed and moved {latest_file} to used directory.")

        return encoded_image
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return None

# Directories
source_dir = r"D:\sentiMation\generators\sketch2life\assets\sketch"
used_dir = r"D:\sentiMation\generators\sketch2life\assets\sketch\used"

# Process the latest image from \assets\sketch\ directory
latest_image_encoded = process_latest_image(source_dir, used_dir)
if latest_image_encoded is None:
    logging.error("Failed to process the latest image.")
    # Handle the error appropriately

control_net_args = {
    "input_image": latest_image_encoded,
    "resize_mode": "Just Resize",
    "module": "lineart_standard",
    "model": "control_v11p_sd15_lineart_fp16 [5c23b17d]",
    "weight": 1,
    "pixel_perfect": True
}

# API and JSON Payload configuration
api_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

json_payload = {
    "prompt": generate_skl_prompt(),
    "negative_prompt": "bad quality, deformed, boring, pixelated, grainy, mutation, artifacts, high contrast",
    "seed": -1,
    "sampler_name": "Euler a",
    "batch_size": 1,
    "steps": 30,
    "cfg_scale": 7,
    "width": 512,
    "height": 690,
    "alwayson_scripts": {
        "ControlNet": {"args": [control_net_args]}
    }
}

# Make the API request
response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=json_payload)

# Processing the response
if response.status_code == 200:
    response_json = response.json()
    base64_image = response_json['images'][0]
    image_bytes = base64.b64decode(base64_image)
    file_path = "D:\\sentiMation\\generators\\sketch2life\\assets\\cn_skl.png"
    with open(file_path, "wb") as image_file:
        image_file.write(image_bytes)
    logging.info("Image generated and saved successfully.")
else:
    logging.error(f"API call failed. Status Code: {response.status_code}, Response: {response.text}")
