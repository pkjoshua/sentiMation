import requests
import logging
import os
import base64

script_dir = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(filename=os.path.join(script_dir, 'gen.log'), level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

# Updated paths to directly use selected_video.mp4 and selected_prompt.txt
generation_dir = os.path.join(script_dir, "assets/generations")
vid_file = os.path.join(script_dir, "chosen_video.mp4")
prompt_file_path = os.path.join(script_dir, "chosen_prompt.txt")

os.makedirs(generation_dir, exist_ok=True)

# Check if the selected video file exists
if not os.path.exists(vid_file):
    logging.error("chosen_video.mp4 not found.")
    exit(1)

# Load the selected prompt
if not os.path.exists(prompt_file_path):
    logging.error("chosen_prompt.txt not found.")
    exit(1)

with open(prompt_file_path, 'r') as file:
    prompt = file.read().strip()

control_net_args = [{
    "resize_mode": "Crop and Resize",   
    "module": "normal_bae",
    "model": "control_v11p_sd15_normalbae_fp16 [592a19d8]",
    "weight": 0.75,
    "pixel_perfect": True,
    "control_mode": "Balanced"
}]

animate_diff_args = {
    "model": "mm_sd_v15_v2.ckpt",
    "format": ['MP4'],
    "enable": True,
    "video_length": 0,
    "fps": 30,
    "loop_number": 0,
    "closed_loop": "N",
    "batch_size": 32,
    "stride": 3,
    "video_source": vid_file,
    "overlap": -1,
    "interp": "NO",
    "interp_x": 10,
    "latent_power": 1,
    "latent_scale": 32
}

json_payload = {
    "prompt": prompt,
    "batch_size": 1,
    "negative_prompt": "bad quality, deformed, boring, pixelated, blurry, unclear, artifact, nude, nsfw",
    "sampler_name": "DDIM",
    "steps": 12,
    "cfg_scale": 8,
    "width": 360,
    "height": 640,
    "alwayson_scripts": {
        "AnimateDiff": {"args": [animate_diff_args]},
        "ControlNet": {"args": control_net_args}
    }
}

logging.info("Sending request with common prompt for all images.")

response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=json_payload)

if response.status_code == 200:
    r = response.json()
    if 'images' in r and r['images']:
        for index, base64_data in enumerate(r['images']):
            mp4_data = base64.b64decode(base64_data)
            output_path = os.path.join(generation_dir, f"generation_{index:04d}.mp4")
            with open(output_path, 'wb') as file:
                file.write(mp4_data)
            logging.info(f"MP4 file saved as {output_path}.")
    else:
        logging.error("No image data found in the response.")
else:
    logging.error(f"API call failed. Status Code: {response.status_code}, Response: {response.text}")
