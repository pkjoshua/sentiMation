import os
import requests
import base64
import json
import logging

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def upscale_image(image_path, api_url, headers, json_payload_template):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    json_payload = json_payload_template.copy()
    json_payload["init_images"] = [encoded_image]

    response = requests.post(api_url, headers=headers, json=json_payload)

    if response.status_code == 200:
        r = response.json()
        if 'images' in r and r['images']:
            base64_data = r['images'][0]
            image_data = base64.b64decode(base64_data)
            return image_data
    else:
        logging.error(f"API call failed for {image_path}. Status Code: {response.status_code}, Response: {response.text}")
        return None

def upscale_images(lowscale_dir, upscale_dir, api_url, headers, json_payload_template):
    image_files = sorted(os.listdir(lowscale_dir))
    for image_file in image_files:
        image_path = os.path.join(lowscale_dir, image_file)
        upscaled_image = upscale_image(image_path, api_url, headers, json_payload_template)
        if upscaled_image:
            output_path = os.path.join(upscale_dir, f"upscaled_{image_file}")
            with open(output_path, 'wb') as file:
                file.write(upscaled_image)
            logging.info(f"Upscaled image saved as {output_path}.")
        else:
            logging.error(f"Failed to upscale image: {image_file}")

# API configuration
api_url = "http://127.0.0.1:7860/sdapi/v1/img2img"
headers = {"Content-Type": "application/json"}

# Define the JSON payload with upscaling script args
json_payload_template = {
    # Prompts
    "prompt": "Best quality, detailed, clear, smooth, sharp",
    "negative_prompt": "Compression artifacts, nudity, nsfw, Bad art, worst quality, low quality, plastic, fake, bad limbs, conjoined, featureless, bad features, incorrect objects, watermark, piercings, logo, watermark, blurry, grainy",
    "batch_size": 1,
    "sampler_name": "DPM++ 2M SDE Karras",
    "steps": 50,
    "cfg_scale": 7,
    "denoising_strength": 0.3,
    "save_images": True,
    "width": 720,
    "height": 1280,
    "script_name": "ultimate sd upscale",
    "script_args": [
        None,           # _ (not used)
        360,            # tile_width
        640,            # tile_height
        8,              # mask_blur
        32,             # padding
        64,             # seams_fix_width
        0.35,           # seams_fix_denoise
        32,             # seams_fix_padding
        5,              # upscaler_index
        True,           # save_upscaled_image a.k.a Upscaled
        0,              # redraw_mode
        False,          # save_seams_fix_image a.k.a Seams fix
        8,              # seams_fix_mask_blur
        0,              # seams_fix_type
        0,              # target_size_type
        720,            # custom_width
        1280,           # custom_height
        2               # custom_scale
    ]
}

# Directories
lowscale_dir = "lowscale"
upscale_dir = "assets\\upscale"
os.makedirs(lowscale_dir, exist_ok=True)
os.makedirs(upscale_dir, exist_ok=True)

# Upscale images
upscale_images(lowscale_dir, upscale_dir, api_url, headers, json_payload_template)
