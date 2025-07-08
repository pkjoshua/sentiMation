from PIL import Image, ExifTags
import base64
import requests
import json

# Function to reorient image
def reorient_image(input_path, output_path):
    img = Image.open(input_path)
    
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation]=='Orientation':
            break

    try:
        exif=dict(img._getexif().items())
        if exif[orientation] == 3:
            img=img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img=img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img=img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # When no orientation EXIF data
        pass
    
    img.save(output_path)

# Correct the orientation
input_path = os.environ.get("TEST_IMG_INPUT", "image.png")
output_path = os.environ.get("TEST_IMG_OUTPUT", "touched_image.JPG")
reorient_image(input_path, output_path)

# Read reoriented image file from disk
with open(output_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/img2img"

# Define the JSON payload
json_payload = {
    "prompt": "cute, demon girl, sexy, revealing, detailed, portrait, cleavage",
    "negative_prompt": "bad quality, deformed, boring",
    "resize_mode": 0,
    "batch_size": 1,
    "steps": 50,
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "denoising_strength": 0.8,
    "init_images": [encoded_image],
    "alwayson_scripts": {
        "controlnet": {
            "args": [
                {
                    "module": "canny",
                    "model": "control_v11p_sd15_canny_fp16 [b18e0966]"
                }
            ]
        }
    }
}

# Define headers
headers = {
    "Content-Type": "application/json"
}

# Make the API request
response = requests.post(api_url, headers=headers, json=json_payload)

# Parse the JSON response
response_json = response.json()

# Decode base64 image to bytes
image_bytes = base64.b64decode(response_json['images'][0])

# Define the file path
file_path = os.environ.get("IMG2IMG_OUTPUT", "img2img_cn.jpg")

# Write the bytes to a file
with open(file_path, "wb") as image_file:
    image_file.write(image_bytes)
