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
        lines = file.readlines()
    prompts = [line.strip().replace("Prompt: ", "") for line in lines if line.startswith("Prompt:")]
    return prompts

# Read all ControlNet images and corresponding prompts
controlnet_dir = "assets\\controlnet"
generation_dir = "assets\\generations"
os.makedirs(generation_dir, exist_ok=True)

controlnet_images = sorted(os.listdir(controlnet_dir))
prompts = read_prompts("selected_story.txt")

for index, (image_name, prompt) in enumerate(zip(controlnet_images, prompts)):
    encoded_image = encode_image_to_base64(os.path.join(controlnet_dir, image_name))
    prompt_text = prompt.strip()
    
    control_net_args = {
        "resize_mode" : "Crop and Resize",
        "module": "tile_colorfix",
        "model": "control_v11f1e_sd15_tile_fp16 [3b860298]",
        "weight": 1,
        "pixel_perfect": True,
        "control_mode" :"Balanced"
    }

    animate_diff_args = {
        "model": "animatediffMotion_v15V2.ckpt",
        "format": ['MP4'],
        "enable": True,
        "video_length": 60,
        "fps": 30,
        "loop_number": 0,
        "closed_loop": "A",
        "batch_size": 16,
        "stride": 1,
        "overlap": -1,
        "interp": "NO",
        "interp_x": 10,
        "latent_power": 0.5,      # Latent power
        "latent_scale": 32,     # Latent scale
        "last_frame": encoded_image,     # Optional last frame
        "latent_power_last": 0.5, # Optional latent power for last frame
        "latent_scale_last": 32
    }

    # Define the JSON payload
    json_payload = {
        "init_images": [encoded_image],
        "denoising_strength": 0.78,
        "prompt": prompt_text,
        "negative_prompt": "bad quality, deformed, boring, pixelated, blurry, unclear, artifact, nude, nsfw",
        "batch_size": 1,
        "sampler_name": "Euler a",
        "steps": 25,
        "cfg_scale": 20,
        "width": 360,
        "height": 640,
        "alwayson_scripts": {
            "AnimateDiff": {"args": [animate_diff_args]},
            "ControlNet": {"args": [control_net_args]}
        }
    }

    # Log the prompt being used
    logging.info(f"Generating with prompt: {prompt_text}")

    # Call the API
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
