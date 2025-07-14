import cv2
import os
import requests
import base64
import json
import logging
from moviepy.editor import ImageSequenceClip

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def upscale_frame(frame_path, api_url, headers, json_payload_template):
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

def extract_frames(video_path, output_dir):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    while success:
        frame_path = os.path.join(output_dir, f"frame{count}.png")
        cv2.imwrite(frame_path, image)     
        success, image = vidcap.read()
        count += 1
    
    return count  # Return the total number of frames extracted

def process_video(video_path, lowscale_dir, upscale_dir, api_url, headers, json_payload_template):
    # Extract frames from the video
    frame_count = extract_frames(video_path, lowscale_dir)

    # Upscale each frame
    for i in range(frame_count):
        frame_path = os.path.join(lowscale_dir, f"frame{i}.png")
        upscaled_image = upscale_frame(frame_path, api_url, headers, json_payload_template)
        if upscaled_image:
            with open(os.path.join(upscale_dir, f"upscaled_frame{i}.png"), 'wb') as file:
                file.write(upscaled_image)

    # Combine upscaled frames back into a video
    frame_files = [os.path.join(upscale_dir, f"upscaled_frame{i}.png") for i in range(frame_count)]
    clip = ImageSequenceClip(frame_files, fps=24)  # Adjust fps to match original video's fps
    clip.write_videofile(os.path.join(upscale_generations_dir, os.path.basename(video_path)), codec="libx264")

# API configuration
from sd_api_config import get_api_url
api_url = get_api_url('img2img')
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
generation_dir = "assets/generations"
lowscale_dir = "assets/lowscale"
upscale_dir = "assets/upscale"
upscale_generations_dir = "assets/upscale_generations"
os.makedirs(lowscale_dir, exist_ok=True)
os.makedirs(upscale_dir, exist_ok=True)
os.makedirs(upscale_generations_dir, exist_ok=True)

# Process each video in the generations directory
for video_name in os.listdir(generation_dir):
    video_path = os.path.join(generation_dir, video_name)
    process_video(video_path, lowscale_dir, upscale_dir, api_url, headers, json_payload_template)
    logging.info(f"Processed video: {video_path}")
