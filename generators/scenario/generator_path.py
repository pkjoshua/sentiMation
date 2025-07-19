import requests
import base64
import json
import logging
import os

logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/img2img"

# Function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

controlnet_dir = "assets\\init"
generation_dir = "assets\\generations"
os.makedirs(generation_dir, exist_ok=True)

# Encode all images in the directory to base64 and store them in a list
controlnet_images = sorted(os.listdir(controlnet_dir))
encoded_images = [encode_image_to_base64(os.path.join(controlnet_dir, img)) for img in controlnet_images]

control_net_args = [{
    "resize_mode": "Just Resize",
    "module": "normal_bae",
    "model": "control_v11f1p_sd15_depth_fp16 [4b72d323]",
    "weight": 1,
    "pixel_perfect": True,
    "control_mode": "Balanced"
}]

animate_diff_args = {
    "model": "mm_sd_v15_v2.ckpt",
    "format": ['MP4'],
    "enable": True,
    "video_length": 60,
    "fps": 30,
    "loop_number": 0,
    "closed_loop": "N",
    "batch_size": 16,
    "stride": 1,
    "overlap": -1,
    "interp": "NO",
    "interp_x": 10
}

json_payload = {
    "init_images": encoded_images,
    "denoising_strength": 0.8,
    "prompt": " <lora:Lora_MC:1>  ARMOR, best quality, detailed, high contrast",
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
