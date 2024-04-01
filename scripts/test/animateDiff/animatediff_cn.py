import requests
import json
import logging
import os
import base64

logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

controlnet_dir = "assets\\init"
generation_dir = "assets\\generations"
batch_dir = "D\\sentiMation\generators\dogshow\assets\test"
vid_file = "/mnt/d/test.mp4"

os.makedirs(generation_dir, exist_ok=True)

# Get full file paths for all images in the directory
controlnet_images = sorted(os.listdir(controlnet_dir))
image_file_paths = [os.path.join(controlnet_dir, img) for img in controlnet_images]

control_net_args = [{
    "resize_mode": "Just Resize",
    "module": "normal_bae",
    "model": "control_v11p_sd15_normalbae_fp16 [592a19d8]",
    "weight": 0.85,
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
    "batch_size": 16,
    "stride": 1,
    "video_source": "/mnt/d/test.mp4",
    "overlap": -1,
    "interp": "NO",
    "interp_x": 10,
    "latent_power": 0.2,
    "latent_scale": 92
}

json_payload = {
    "prompt": "  ARMOR, best quality, detailed, high contrast",
    "batch_size": 60,
    "negative_prompt": "bad quality, deformed, boring, pixelated, blurry, unclear, artifact, nude, nsfw",
    "batch_size": 1,
    "sampler_name": "DDIM",
    "steps": 20,
    "cfg_scale": 10,
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
