import os
import requests
import base64
import json
import logging
import cv2
import imageio  

# Initialize logging with path relative to script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename=os.path.join(script_dir, "gen.log"), level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

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
    return count, fps

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

def process_video(video_path, lowscale_dir, upscale_dir, api_url, headers, json_payload_template, upscale_vids_dir):
    is_gif = video_path.endswith('.gif')
    if is_gif:
        reader = imageio.get_reader(video_path)
        fps = 30
        frame_count = 0
        for i, frame in enumerate(reader):
            frame_path = os.path.join(lowscale_dir, f"frame{frame_count:04d}.png")
            imageio.imwrite(frame_path, frame)
            frame_count += 1
    else:
        frame_count, fps = extract_frames(video_path, lowscale_dir)
    for i in range(frame_count):
        frame_path = os.path.join(lowscale_dir, f"frame{i:04d}.png")
        upscaled_image = upscale_frame(frame_path, api_url, headers, json_payload_template)
        if upscaled_image:
            with open(os.path.join(upscale_dir, f"upscaled_frame{i:04d}.png"), 'wb') as file:
                file.write(upscaled_image)
    output_video_name = os.path.basename(video_path).split('.')[0] + '_upscaled.mp4'
    output_video_path = os.path.join(upscale_vids_dir, output_video_name)
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
        2,              # upscaler_index
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

# Adjusted directories to use the script directory as base
vids_dir = os.path.join(script_dir, "assets", "vids")
lowscale_dir = os.path.join(script_dir, "assets", "lowscale")
upscale_dir = os.path.join(script_dir, "assets", "upscale")
upscale_vids_dir = os.path.join(script_dir, "assets", "upscale_vids")

os.makedirs(lowscale_dir, exist_ok=True)
os.makedirs(upscale_dir, exist_ok=True)
os.makedirs(upscale_vids_dir, exist_ok=True)

for video_file in sorted(os.listdir(vids_dir)):
    video_path = os.path.join(vids_dir, video_file)
    if video_path.endswith('.mp4') or video_path.endswith('.gif'):
        logging.info(f"Processing video: {video_path}")
        process_video(video_path, lowscale_dir, upscale_dir, api_url, headers, json_payload_template, upscale_vids_dir) # This should be replaced with actual video processing loop/logic
video_path = os.path.join(vids_dir, video_file)
if video_path.endswith('.mp4') or video_path.endswith('.gif'):
    logging.info(f"Processing video: {video_path}")
    process_video(video_path, lowscale_dir, upscale_dir, api_url, headers, json_payload_template, upscale_vids_dir)
