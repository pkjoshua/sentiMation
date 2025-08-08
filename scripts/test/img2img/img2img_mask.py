from PIL import Image
import base64
import requests
import json

def create_mask(image_path, mask_path):
    # Function to create a mask (black for transparent, white for non-transparent)
    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        new_data = []
        for item in img.getdata():
            if item[3] == 0:  # Transparent pixels
                new_data.append((0, 0, 0, 255))  # Black
            else:
                new_data.append((255, 255, 255, 255))  # White
        img.putdata(new_data)
        img = img.convert("RGB")
        img.save(mask_path)

# Paths
image_path = "bulbasaur.png"
mask_path = "bulbasaur_mask.png"

# Create mask
create_mask(image_path, mask_path)

# Read and encode image and mask
with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

with open(mask_path, "rb") as mask_file:
    mask_image = base64.b64encode(mask_file.read()).decode()

# Define the API URL and payload
api_url = "http://host.docker.internal:7860/sdapi/v1/img2img"
json_payload = {
    "prompt": "A detailed mandala with symmetrical patterns, creating a hypnotic effect, digital painting, pixiv, concept art, 3d, by Simon Cowell, Ricardo Ow and Tom Cross",
    "negative_prompt": "bad quality, deformed, boring",
    "resize_mode": 0,
    "batch_size": 1,
    "steps": 50,
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "denoising_strength": 0.8,
    "init_images": [encoded_image],
    "mask": mask_image
}

# Define headers
headers = {
    "Content-Type": "application/json"
}

# Make the API request
response = requests.post(api_url, headers=headers, json=json_payload)

# Parse the JSON response
if response.status_code == 200:
    response_json = response.json()
    image_bytes = base64.b64decode(response_json['images'][0])

    # Define the file path and save the image
    file_path = "gen.png"
    with open(file_path, "wb") as image_file:
        image_file.write(image_bytes)
else:
    print(f"Error: {response.status_code}, {response.text}")
