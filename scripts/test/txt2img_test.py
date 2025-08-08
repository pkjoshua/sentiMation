import requests
import json
import base64

# Define the API URL
api_url = "http://host.docker.internal:7860/sdapi/v1/txt2img"

# Define the JSON payload
json_payload = {
    "prompt": "bunny, female, girl, beautiful, skimpy, revealing, detailed, portrait",
    "negative_prompt": "bad quality, deformed, boring",
    "seed": -1,
    "sampler_name": "DDIM",
    "batch_size": 1,
    "steps": 10,
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "denoising_strength": 0.8
}

# Convert the payload to JSON format
json_payload_str = json.dumps(json_payload)

# Define the headers
headers = {
    "Content-Type": "application/json"
}

# Make the API request
response = requests.post(api_url, headers=headers, data=json_payload_str)

# Parse the JSON response
response_json = response.json()

# Extract the base64 encoded image data from the 'images' field
base64_image = response_json['images'][0]  # Assumes the first element in the 'images' array contains the base64 image data

# Decode the base64 image to bytes
image_bytes = base64.b64decode(base64_image)

# Define the file path
file_path = os.environ.get("OUTPUT_IMAGE", "your_image.png")

# Write the bytes to a file
with open(file_path, "wb") as image_file:
    image_file.write(image_bytes)
