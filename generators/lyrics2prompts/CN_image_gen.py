import requests
import json
import logging
import base64
import os

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Read prompts from selected_story.txt
def read_prompts_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        prompts = [line.split('Prompt: ')[-1].strip() for line in lines if line.startswith('Prompt: ')]
    return prompts

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

# Process and save the image
def process_and_save_image(base64_image, file_index, output_dir):
    image_bytes = base64.b64decode(base64_image)
    file_path = os.path.join(output_dir, f"controlnet_image_{file_index:04d}.png")
    with open(file_path, "wb") as image_file:
        image_file.write(image_bytes)
    logging.info(f"Saved image at {file_path}")

def make_api_call_and_save(prompt, index, output_dir):
    json_payload = {
        "prompt": prompt,
        "negative_prompt": "bad quality, deformed, boring, pixelated, blurry, unclear, artifact, nude, nsfw",
        "seed": -1,
        "sampler_name": "DDIM",
        "batch_size": 1,
        "steps": 30,
        "cfg_scale": 7,
        "width": 360,
        "height": 640
    }

    response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=json_payload)
    if response.status_code == 200:
        response_json = response.json()
        base64_image = response_json['images'][0]
        process_and_save_image(base64_image, index, output_dir)
    else:
        logging.error(f"API call for prompt '{prompt}' failed with status code {response.status_code}")

# Read prompts
selected_story_file = "selected_story.txt"
prompts = read_prompts_from_file(selected_story_file)

# Output directory
output_dir = "assets\\controlnet"
os.makedirs(output_dir, exist_ok=True)

# Make API calls for each prompt
for index, prompt in enumerate(prompts):
    make_api_call_and_save(prompt, index, output_dir)
