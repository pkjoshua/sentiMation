import os
import requests
import base64
import json
import logging
import cv2
from PIL import Image
import io

# Initialize logging
logging.basicConfig(filename="pokemon_log.log", level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def upscale_frame(frame_path, api_url, headers, json_payload_template, frame_number):
    with open(frame_path, "rb") as image_file:
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
        logging.error(f"API call failed for {frame_path}. Status Code: {response.status_code}, Response: {response.text}")
        return None

def upscale_image(image_path, api_url, headers, json_payload_template):
    with Image.open(image_path) as img:
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

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

def extract_frames(video_path, output_dir):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    while success:
        cv2.imwrite(os.path.join(output_dir, f"frame_{count:04d}.png"), image)
        success, image = vidcap.read()
        count += 1

def create_video_from_frames(frame_folder, output_video_path, fps=30):
    frame_files = sorted([os.path.join(frame_folder, file) for file in os.listdir(frame_folder) if file.endswith('.png')],
                         key=lambda x: int(x.split('_')[2].split('.png')[0]))

    if not frame_files:
        logging.error("No frames found in the folder.")
        return

    frame = cv2.imread(frame_files[0])
    height, width, layers = frame.shape
    size = (width, height)
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    for frame_file in frame_files:
        frame = cv2.imread(frame_file)
        out.write(frame)
    out.release()

# API configuration and directories
api_url = "http://127.0.0.1:7860/sdapi/v1/img2img"
headers = {"Content-Type": "application/json"}
lowscale_video_path = "lowscale.mp4"
lowscale_dir = "lowscale"
upscale_dir = "upscale"
os.makedirs(lowscale_dir, exist_ok=True)
os.makedirs(upscale_dir, exist_ok=True)

# JSON payload for upscaling script
json_payload_template = {
    "prompt": "Best quality, detailed, clear, smooth, sharp",
    "negative_prompt": "Compression artifacts, nudity, nsfw, Bad art, worst quality, low quality, plastic, fake, bad limbs, conjoined, featureless, bad features, incorrect objects, watermark, piercings, logo, watermark, blurry, grainy",
    "batch_size": 1,
    "sampler_name": "DPM++ 2M SDE Karras",
    "steps": 50,
    "cfg_scale": 7,
    "denoising_strength": 0.3,
    "save_images": True,
    "width": 948,
    "height": 948,
    "script_name": "ultimate sd upscale",
    "script_args": [
        None,           # _ (not used)
        474,            # tile_width
        474,            # tile_height
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
        948,            # custom_width
        948,           # custom_height
        2              # custom_scale
    ]
}

# Extract frames from lowscale.mp4
extract_frames(lowscale_video_path, lowscale_dir)

# Upscale each extracted frame
for i, frame_file in enumerate(sorted(os.listdir(lowscale_dir))):
    frame_path = os.path.join(lowscale_dir, frame_file)
    upscaled_image = upscale_frame(frame_path, api_url, headers, json_payload_template, i)
    if upscaled_image:
        with open(os.path.join(upscale_dir, f"upscaled_{frame_file}"), 'wb') as file:
            file.write(upscaled_image)

# Upscale the current_pokemon.png image
pokemon_image_path = "current_pokemon.png"
upscaled_pokemon_image = upscale_image(pokemon_image_path, api_url, headers, json_payload_template)
if upscaled_pokemon_image:
    with open("current_pokemon_upscale.png", 'wb') as file:
        file.write(upscaled_pokemon_image)
    logging.info("Upscaled current_pokemon.png successfully.")
else:
    logging.error("Failed to upscale current_pokemon.png.")

# Upscale the current_mask.png image
pokemon_image_path = "current_mask.png"
upscaled_pokemon_image = upscale_image(pokemon_image_path, api_url, headers, json_payload_template)
if upscaled_pokemon_image:
    with open("current_mask_upscale.png", 'wb') as file:
        file.write(upscaled_pokemon_image)
    logging.info("Upscaled current_mask.png successfully.")
else:
    logging.error("Failed to upscale current_mask.png.")

# Create an MP4 from the upscaled frames
create_video_from_frames(upscale_dir, "upscale.mp4")
