import requests
import base64
import json
import logging
import os

logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Define the API URL
api_url = "http://host.docker.internal:7860/sdapi/v1/img2img"

# Function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to read prompts from selected_story.txt
def read_prompts(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]

controlnet_dir = "assets\\init"
generation_dir = "assets\\generations"
os.makedirs(generation_dir, exist_ok=True)

controlnet_images = sorted(os.listdir(controlnet_dir))
prompts = read_prompts("prompt.txt")

for index, (image_name, prompt) in enumerate(zip(controlnet_images, prompts)):
    encoded_image = encode_image_to_base64(os.path.join(controlnet_dir, image_name))
    prompt_text = prompt.strip()

    animate_diff_args = {
        "model": "animatediffMotion_v15V2.ckpt",
        "format": ['MP4'],
        "enable": True,
        "video_length": 150,
        "fps": 20,
        "loop_number": 0,
        "closed_loop": "N",
        "batch_size": 16,
        "stride": 1,
        "overlap": -1,
        "interp": "NO",
        "interp_x": 10,
        "latent_power": 0.5,
        "latent_scale": 32,
        "last_frame": encoded_image,
        "latent_power_last": 0.5,
        "latent_scale_last": 32
    }

    json_payload = {
        "init_images": [encoded_image],
        "denoising_strength": 0.9,
        "prompt": prompt_text,
        "negative_prompt": "bad quality, deformed, boring, pixelated, blurry, unclear, artifact, nude, nsfw",
        "batch_size": 1,
        "sampler_name": "DPM++ 2M Karras",
        "steps": 20,
        "cfg_scale": 10,
        "width": 360,
        "height": 640,
        "alwayson_scripts": {
            "AnimateDiff": {"args": [animate_diff_args]}
        }
    }

    logging.info(f"Generating with prompt: {prompt_text}")

    response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=json_payload)

    if response.status_code == 200:
        r = response.json()
        if 'images' in r and r['images']:
            base64_data = r['images'][0]
            mp4_data = base64.b64decode(base64_data)
            output_path = os.path.join(generation_dir, f"generation_{index:04d}.mp4")
            with open(output_path, 'wb') as file:
                file.write(mp4_data)
            logging.info(f"MP4 file saved as {output_path}.")
        else:
            logging.error(f"No image data found in the response for prompt: {prompt_text}")
    else:
        logging.error(f"API call failed for prompt: {prompt_text}. Status Code: {response.status_code}, Response: {response.text}")
