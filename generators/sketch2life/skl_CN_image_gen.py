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
        Icy landscape, frozen tundra, glacial beauty, mesmerizing, 4k, high detail
        0: (frost:1.5), (glacial rivers:1.8)
        50: (northern lights:1.5), (starry sky:1.8)
        100: (snowfall:1.5), (pine forests:1.8)
        150: (mountain peaks:1.5), (clear sky:1.8)
        200: (ice caves:1.5), (crystal formations:1.8)
        250: (blizzard:1.5), (wildlife:1.8)"""),

        textwrap.dedent("""\
        Lava flows, volcanic eruption, fiery environment, intense, 4k, high resolution
        0: (eruption:1.5), (smoke:1.8)
        50: (molten rock:1.5), (ash clouds:1.8)
        100: (calm lava flows:1.5), (night sky:1.8)
        150: (renewed eruption:1.5), (flying sparks:1.8)
        200: (cooling lava:1.5), (formation of new land:1.8)
        250: (steam:1.5), (flora growth:1.8)"""),

        textwrap.dedent("""\
        Cyberpunk cityscape, electric, neon lights, futuristic, vibrant, 4k, ultra high definition
        0: (downtown neon:1.5), (hover cars:1.8)
        50: (rooftop gardens:1.5), (city nightlife:1.8)
        100: (underground markets:1.5), (holograms:1.8)
        150: (corporate towers:1.5), (drones:1.8)
        200: (rainy streets:1.5), (neon reflections:1.8)
        250: (virtual reality zones:1.5), (cybernetic enhancements:1.8)"""),

        textwrap.dedent("""\
        Steampunk world, gears and steam, vintage technology, intricate, 4k, sharp details
        0: (airships:1.5), (cobbled streets:1.8)
        50: (inventors' workshops:1.5), (mechanical animals:1.8)
        100: (steam trains:1.5), (iron bridges:1.8)
        150: (clock towers:1.5), (foggy alleys:1.8)
        200: (brass instruments:1.5), (leather attire:1.8)
        250: (hidden taverns:1.5), (secret meetings:1.8)"""),

        textwrap.dedent("""\
        Desert dunes, arid climate, sandstorm, vast, mesmerizing, 4k, high clarity
        0: (daylight:1.5), (travelers:1.8), (camels:2.0)
        50: (oasis:1.5), (palm trees:1.8), (refreshing water:2.0)
        100: (sandstorm:1.5), (shelter:1.8), (survival:2.0)
        150: (evening calm:1.5), (campfire:1.8), (star gazing:2.0)
        200: (full moon:1.5), (cool night:1.8), (nocturnal creatures:2.0)
        250: (dawn:1.5), (golden sunrise:1.8), (new journey:2.0)"""),

        textwrap.dedent("""\
        Beach paradise, tropical, sunny, ocean view, serene, beautiful, 4k, cinematic
        0: (sunny beach:1.5), (palm trees:1.8), (clear water:2.0)
        50: (coral reefs:1.5), (colorful fish:1.8), (underwater world:2.0)
        100: (sunset:1.5), (silhouettes:1.8), (relaxing vibes:2.0)
        150: (beach party:1.5), (music and dance:1.8), (joyful moments:2.0)
        200: (starry night:1.5), (bonfire:1.8), (stories shared:2.0)
        250: (sunrise:1.5), (morning yoga:1.8), (rejuvenation:2.0)""")
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
    "module": "canny",
    "model": "control_v11p_sd15_canny_fp16 [b18e0966]",
    "weight": 1,
    "pixel_perfect": True
}

# API and JSON Payload configuration
api_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

json_payload = {
    "prompt": generate_skl_prompt(),
    "negative_prompt": "bad quality, deformed, boring, pixelated, grainy, low contrast, mutation, artifacts",
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
