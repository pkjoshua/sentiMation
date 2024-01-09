import requests
import base64
import json
import logging
import os

# Function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to read prompt
def read_prompt(file_path):
    with open(file_path, "r") as file:
        return file.readline().strip()

# Read prompt from file
prompt = read_prompt("chosen_prompt.txt")

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/img2img"

# Directory containing frames
frames_dir = "assets\\frames"

# Encode all frames in the directory to base64
base64_frames = [encode_image_to_base64(os.path.join(frames_dir, frame_file))
                 for frame_file in sorted(os.listdir(frames_dir))
                 if frame_file.endswith(('.png', '.jpg', '.jpeg'))]

# Set up logging
logging.basicConfig(filename="api_call.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Define the JSON payload
json_payload = {
    "init_images": [base64_frames[0]], 
    "resize_mode": "Crop and resize", 
    "denoising_strength": 0.85,
    "include_init_images": True,
    "prompt": prompt,
    "negative_prompt": "bad quality, deformed, boring, pixelated, blurry, unclear, artifact, nude, nsfw, humans, human hands",
    "batch_size": 1,
    "seed": -1,
    "sampler_name": "DPM++ 2M Karras",
    "steps": 20,
    "cfg_scale": 11,
    "width": 360,
    "mask": None,
    "height": 640,
    "script_name": "Multi-frame Video - V0.72-beta (josh version)",
    "script_args": [
    None,
    "D:\sentiMation\multi_test", 
    0.85,
    "FirstGen",
    True,
    False,
    False,
    1,
    1,
    "InputFrame"]
}

# Call the API
response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=json_payload)

# Save API response as a text file
response_file = "api_response.txt"
with open(response_file, 'w') as file:
    file.write(json.dumps(response.json(), indent=4))

# Check the response
if response.status_code == 200:
    logging.info("API call successful.")
else:
    logging.error(f"API call failed. Status Code: {response.status_code}, Response: {response.text}")
