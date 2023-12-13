import requests
import base64
import json

# Read reoriented image file from disk
with open("image.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

# Define the payload
json_payload = {
    "prompt": "cute, demon girl, sexy, revealing, detailed, portrait, cleavage",
    "negative_prompt": "bad quality, deformed, boring",
    "batch_size": 1,
    "steps": 50,
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "denoising_strength": 0.8,
    "alwayson_scripts": {
        "AnimateDiff": {
            "args": [
                {
                    "model": "mm_sd_v15_v2.ckpt",
                    "format": ["GIF"],
                    "enable": True,
                    "video_length": 16,
                    "fps": 8,
                    "loop_number": 0,
                    "closed_loop": "R+P",
                    "batch_size": 16,
                    "stride": 1,
                    "overlap": -1,
                    "interp": "Off",
                    "interp_x": 10,
                    "latent_power": 1,
                    "latent_scale": 32,
                    "last_frame": None,
                    "latent_power_last": 1,
                    "latent_scale_last": 32
                }
            ]
        }
    }
}

# Define headers
headers = {
    "Content-Type": "application/json"
}

# Call the API
response = requests.post(api_url, headers=headers, json=json_payload)

# Debugging
print("Full API Response:", response.json())
print("HTTP Status Code:", response.status_code)

try:
    response_json = response.json()
    base64_image = response_json['images'][0]  # Assumes the first element in the 'images' array contains the base64 image data
except KeyError:
    print("Key 'images' not found in the API response.")

# Decode base64 image to bytes
image_bytes = base64.b64decode(base64_image)

# Define file path
file_path = "D://api_output/gif.gif"  # Replace with the desired file name

# Write bytes to file
with open(file_path, "wb") as image_file:
    image_file.write(image_bytes)
