import requests
import base64
import json
import logging
import os

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
generation_dir = "assets\\image_generations"
os.makedirs(generation_dir, exist_ok=True)

frame_files = sorted(os.listdir(frames_dir))
previous_generation = ""
second_previous_generation = ""

for index, frame_file in enumerate(frame_files):
    init_image = encode_image_to_base64(os.path.join(frames_dir, frame_file))

    # Initial control_net_args configuration
    control_net_args = [{
        "resize_mode" : "Just Resize",
        "module": "tile_resample",
        "model": "control_v11f1e_sd15_tile_fp16 [3b860298]",
        "weight": 0.7,
        "pixel_perfect": True,
        "control_mode": "ControlNet is more important"
    }]

    # Modify control_net_args based on the run
    if index > 0:
        control_net_args[0]["input_image"] = previous_generation
        if index > 1:
            control_net_args.append({
                "input_image": second_previous_generation,
                "resize_mode": "Just Resize",
                "module": "reference_only",
                "weight": 0.9,
                "pixel_perfect": True,
                "control_mode": "ControlNet is more important"
            })

    # Define the JSON payload
    json_payload = {
        "init_images": [init_image],
        "denoising_strength": 0.3,
        "include_init_images": True,
        "prompt": prompt,
        "negative_prompt": "bad quality, deformed, boring, pixelated, blurry, unclear, artifact, nude, nsfw",
        "batch_size": 1,
        "sampler_name": "DDIM",
        "steps": 12,
        "cfg_scale": 10,
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

            output_path = os.path.join(generation_dir, f"generation_{index:04d}.jpg")
            with open(output_path, 'wb') as file:
                file.write(image_data)
            logging.info(f"Image saved as {output_path}.")

            # Update generation variables for next iteration
            second_previous_generation = previous_generation
            previous_generation = base64_data
        else:
            logging.error(f"No image data found in the response for frame: {frame_file}")
    else:
        logging.error(f"API call failed for frame: {frame_file}. Status Code: {response.status_code}, Response: {response.text}")
