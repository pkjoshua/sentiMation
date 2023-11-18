import requests
import base64
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename="pokemon_cards_log.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Function to read the chosen prompt from a file
def read_chosen_prompt():
    with open("chosen_prompt.txt", "r") as f:
        chosen_prompt = f.read().strip()
        logging.info(f"Chosen prompt: {chosen_prompt}")
        return chosen_prompt

# Read and encode the test image
with open("test.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

# Define the API URL for upscaling (modify if different from img2img)
api_url = "http://127.0.0.1:7860/sdapi/v1/img2img" # Update this if needed

# Define the JSON payload with upscaling script args
json_payload = {
    "init_images": [encoded_image],
    "prompt": "Best quality, detailed, clear, smooth, sharp, ",
    "negative_prompt": "Compression artifacts, nudity, nsfw, Bad art, worst quality, low quality, plastic, fake, bad limbs, conjoined, featureless, bad features, incorrect objects, watermark, piercings, logo, watermark, blurry, grainy",
    "batch_size": 1,
    "sampler_name": "DPM++ 2M SDE Karras",
    "steps": 50,
    "cfg_scale": 7,
    "denoising_strength": 0.3,
    "save_images": True,
    "width": 980,
    "height": 1368,
    "script_name": "ultimate sd upscale",
    "script_args": [
        None,       # _ (not used)
        490,        # tile_width
        684,        # tile_height
        8,          # mask_blur
        32,         # padding
        64,         # seams_fix_width
        0.35,       # seams_fix_denoise
        32,         # seams_fix_padding
        5,          # upscaler_index
        True,       # save_upscaled_image a.k.a Upscaled
        0,          # redraw_mode
        False,      # save_seams_fix_image a.k.a Seams fix
        8,          # seams_fix_mask_blur
        0,          # seams_fix_type
        0,          # target_size_type
        980,       # custom_width
        1368,       # custom_height
        2           # custom_scale
    ]
}

# Define headers
headers = {
    "Content-Type": "application/json"
}

# Call the API for upscaling
response = requests.post(api_url, headers=headers, json=json_payload)

# Check for successful response
if response.status_code == 200:
    r = response.json()
    # Assuming 'images' key contains a list of base64 encoded strings
    if 'images' in r and r['images']:
        base64_data = r['images'][0]
        
        # Decode base64 (assuming the data is direct base64 of PNG)
        image_data = base64.b64decode(base64_data)

        # Write the image data to a file
        with open('upscale.png', 'wb') as file:
            file.write(image_data)
        print("Image file saved as 'upscale.png'.")
    else:
        print("No image data found in the response.")
else:
    print(f"API call failed. Status Code: {response.status_code}, Response: {response.text}")

# Debugging and Logging
if response.status_code == 200:
    logging.info(f"API call successful. Status Code: {response.status_code}")
    response_json = response.json()
    # Further processing can be done here, such as saving the upscaled image
else:
    logging.error(f"API call failed. Status Code: {response.status_code}, Response: {response.text}")
