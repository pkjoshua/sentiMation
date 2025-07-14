import requests
import base64
import json
import logging
import os

logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Define the API URL
from sd_api_config import get_api_url
api_url = get_api_url('img2img')

# Function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Read settings from the JSON file
input_dir = 'assets/inputs'
with open(os.path.join(input_dir, 'settings.json'), 'r') as file:
    settings = json.load(file)

user_prompt = settings['user_prompt']
user_negative_prompt = settings['user_negative_prompt']

init_dir = "assets/init"
generation_dir = "assets/generations"
os.makedirs(generation_dir, exist_ok=True)

init_images = sorted(os.listdir(init_dir))

for index, image_name in enumerate(init_images):
    encoded_image = encode_image_to_base64(os.path.join(init_dir, image_name))

    animate_diff_args = {
        "model": "mm_sd_v15_v2.ckpt",
        "format": ['MP4'],
        "enable": True,
        "video_length": 60,
        "fps": 20,
        "loop_number": 0,
        "closed_loop": "R-P",
        "batch_size": 16,
        "stride": 1,
        "overlap": -1,
        "interp": "NO",
        "interp_x": 10,
        "latent_power": 0.2,
        "latent_scale": 92,
        "last_frame": encoded_image,
        "latent_power_last": 0.2,
        "latent_scale_last": 92
    }

        # Modified control_net_args configuration
    control_net_args = {
        "input_image": encoded_image,
        "resize_mode": "Just Resize",
        "module": "depth_midas",
        "model": "control_v11f1p_sd15_depth_fp16 [4b72d323]",
        "weight": 1.0,
        "pixel_perfect": True,
        "control_mode": "Balanced"
    }


    json_payload = {
        "init_images": [encoded_image],
        "denoising_strength": 0.75,
        "prompt": user_prompt,
        "negative_prompt": user_negative_prompt,
        "batch_size": 1,
        "sampler_name": "DPM++ 2M Karras",
        "steps": 25,
        "cfg_scale": 10,
        "width": 360,
        "height": 640,
        "alwayson_scripts": {
            "AnimateDiff": {"args": [animate_diff_args]},
            "ControlNet": {"args": [control_net_args]}
        }
    }

    logging.info(f"Generating with prompt: {user_prompt}")

    response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=json_payload)

    if response.status_code == 200:
        r = response.json()
        if 'images' in r and r['images']:
            base64_data = r['images'][0]
            mp4_data = base64.b64decode(base64_data)
            output_path = os.path.join(generation_dir, f"generation_{index:04d}.mp4")
            with open(output_path, 'wb') as file:
                file.write(mp4_data)
            logging.info(f"MP4 file saved as {output_path}.")
        else:
            logging.error("No image data found in the response.")
    else:
        logging.error(f"API call failed. Status Code: {response.status_code}, Response: {response.text}")