import cv2
import os
import requests
import base64
import json
import logging
import cv2

# Initialize logging
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
        frame_path = os.path.join(output_dir, f"frame{count:04d}.png")
        cv2.imwrite(frame_path, image)     
        success, image = vidcap.read()
        count += 1
    
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    return count, fps  # Return the total number of frames extracted and the fps

def create_video_from_frames(frame_folder, output_video_path, fps):
    frame_files = sorted([os.path.join(frame_folder, file) for file in os.listdir(frame_folder) if file.endswith('.png')])
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

def process_video(video_path, lowscale_dir, upscale_dir, api_url, headers, json_payload_template):
    frame_count, fps = extract_frames(video_path, lowscale_dir)
    for i in range(frame_count):
        frame_path = os.path.join(lowscale_dir, f"frame{i:04d}.png")
        upscaled_image = upscale_frame(frame_path, api_url, headers, json_payload_template)
        if upscaled_image:
            with open(os.path.join(upscale_dir, f"upscaled_frame{i:04d}.png"), 'wb') as file:
                file.write(upscaled_image)

    # Create the upscaled video
    output_video_path = os.path.join("assets\\upscale_generations", os.path.basename(video_path))
    create_video_from_frames(upscale_dir, output_video_path, fps)

# API configuration
api_url = "http://127.0.0.1:7860/sdapi/v1/img2img"
headers = {"Content-Type": "application/json"}

# Define the JSON payload with upscaling script args
json_payload_template = {
    # Prompts
    "prompt": "Best quality, detailed, clear, smooth, sharp, 4k, high resolution",
    "negative_prompt": "Compression artifacts, nudity, nsfw, Bad art, worst quality, low quality, plastic, fake, bad limbs, conjoined, featureless, bad features, incorrect objects, watermark, piercings, logo, watermark, blurry, grainy",
    "batch_size": 1,
    "sampler_name": "DPM++ 2M SDE Karras",
    "steps": 30,
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
generations_dir = "assets\\generations"
lowscale_dir = "assets\\lowscale"
upscale_dir = "assets\\upscale"
upscale_generations_dir = "assets\\upscale_generations"

os.makedirs(lowscale_dir, exist_ok=True)
os.makedirs(upscale_dir, exist_ok=True)
os.makedirs(upscale_generations_dir, exist_ok=True)

# Process each generation video
for video_file in sorted(os.listdir(generations_dir)):
    video_path = os.path.join(generations_dir, video_file)
    if video_path.endswith('.mp4'):
        logging.info(f"Processing video: {video_path}")
        process_video(video_path, lowscale_dir, upscale_dir, api_url, headers, json_payload_template)
        # Clear lowscale and upscale directories for next video
        for folder in [lowscale_dir, upscale_dir]:
            for file in os.listdir(folder):
                os.unlink(os.path.join(folder, file))
