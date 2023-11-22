import os
import requests
import base64
import json
import logging
import cv2

# Initialize logging
logging.basicConfig(filename="pokemon_log.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

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

def create_video_from_frames(frame_folder, output_video_path, fps=30):
    frame_files = sorted([os.path.join(frame_folder, file) for file in os.listdir(frame_folder) if file.endswith('.png')])
    if not frame_files:
        logging.error("No frames found in the folder.")
        return

    # Get size of the first frame
    frame = cv2.imread(frame_files[0])
    height, width, layers = frame.shape
    size = (width, height)

    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    for frame_file in frame_files:
        frame = cv2.imread(frame_file)
        out.write(frame)
    out.release()

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
    "width": 1422,
    "height": 1422,
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
        1422,            # custom_width
        1422,           # custom_height
        3              # custom_scale
    ]
}

# Directories
overlayed_frames_dir = "overlayed_frames"
upscale_dir = "upscale"
os.makedirs(overlayed_frames_dir, exist_ok=True)
os.makedirs(upscale_dir, exist_ok=True)

# Upscale each frame in the overlayed_frames directory
for frame_file in sorted(os.listdir(overlayed_frames_dir)):
    frame_path = os.path.join(overlayed_frames_dir, frame_file)
    if frame_file.endswith('.png'):
        upscaled_image = upscale_frame(frame_path, api_url, headers, json_payload_template)
        if upscaled_image:
            with open(os.path.join(upscale_dir, f"upscaled_{frame_file}"), 'wb') as file:
                file.write(upscaled_image)

# Create an MP4 from the upscaled frames
create_video_from_frames(upscale_dir, "output.mp4")
