import os
import requests
import base64
import json
import logging
from moviepy.editor import VideoFileClip
from PIL import Image

script_dir = os.path.dirname(os.path.abspath(__file__))  # Path to the script's directory

# Set up logging
logging.basicConfig(filename=os.path.join(script_dir, 'gen.log'), level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def extract_frames_from_video(video_path, frames_dir):
    with VideoFileClip(video_path) as video:
        # Remove the FPS-based conditional, save every frame
        for i, frame in enumerate(video.iter_frames()):
            frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")  # Ensure frame numbering is zero-padded
            frame_image = Image.fromarray(frame)
            frame_image.save(frame_path)

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
            logging.info(f"Upscaled image saved: {output_path}")
        else:
            logging.error(f"Failed to upscale image: {image_file}")

# API configuration
from sd_api_config import get_api_url
api_url = get_api_url('img2img')
headers = {"Content-Type": "application/json"}

# Adjusted paths

generation_dir = os.path.join(script_dir, "assets/generations") 
lowscale_dir = os.path.join(script_dir, "assets/lowscale")
upscale_dir = os.path.join(script_dir, "assets/upscale")  # Directory for used videos

os.makedirs(lowscale_dir, exist_ok=True)
os.makedirs(upscale_dir, exist_ok=True)

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
        720,            # tile_width
        1280,            # tile_height
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

# Assuming there is only one video in the generations directory
video_files = [f for f in os.listdir(generation_dir) if f.endswith('.mp4')]
if video_files:
    video_path = os.path.join(generation_dir, video_files[0])
    # Extract frames
    extract_frames_from_video(video_path, lowscale_dir)
    # Upscale images
    upscale_images(lowscale_dir, upscale_dir, api_url, headers, json_payload_template)
else:
    logging.error("No video file found in the generations directory.")

