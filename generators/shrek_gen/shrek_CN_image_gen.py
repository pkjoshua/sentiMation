import requests
import json
import random
import logging
from datetime import datetime
import base64

# Set up logging
logging.basicConfig(filename='shrek_prompts.log', level=logging.INFO)

# Function to generate Shrek-related prompt
def generate_shrek_prompt():
    prompts = [
        "Shrek fighting a dragon on a volcano, radiant greatsword, epic, dark fantasy, fire, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek dueling a medieval knight, armor, sword, dark fantasy, dark souls, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek driving a futuristic motorcycle through the city, cyberpunk, cyber, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek evading an apocalyptic robot, detailed, 4k, high quality, clear, smooth, cinematic, intense, <lora:shrek:0.2>",
        "Shrek as a king of an alien planet, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek riding a futuristic motorcycle, tron, cyber, blue, virtual world, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek fighting against an alien invasion, above earth, space, starts, cyber, high contrast, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek defeating a golden knight, in a castle, swords, armor, dark fantasy, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek peeling an onion while cooking, in a swamp hut, stove, utencils, kitchen, pans, pot, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>"
        "Shrek eating a banana, jungle, monkeys, trees, vines, luscious jungle, green, vegetation, flowers, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek riding a dinosaur through the mountains, rocky terrain, cliffs, grass, eagles, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek typing at a computer, hacking, blackhat, computer screen, nerdy, soda, moms house, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek hunting a wild boar, fantasy, medieval, spear, tusks, grassland, river, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek golfing at a country club, driver, grass, golf cart, flag, country club in the background, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek as a priest at a church, reading the gospel, (wine:1.2), (bread:1.2), christian, cross, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.2>",
        "Shrek as a yoga instructor, yoga retreat, wooden floor, scenic view, stretching, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.4>",
        "Shrek boiling a large lobster inside of a pot, steam, fire, claws, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.3>",
        "Shrek scrolling on his phone, in a futurisitc city, digital billboards, holograms, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.3>",
        "Shrek writing a best selling novel, at a desk, in a cabin, fireplace, warmth, paper, quill, detailed, 4k, high quality, clear, smooth, cinematic, <lora:shrek:0.3>"
    ]
    chosen_prompt = random.choice(prompts)
    logging.info(f"{datetime.now()} - Chosen prompt: {chosen_prompt}")

    # Write the chosen prompt to a file
    with open("chosen_prompt.txt", "w") as f:
        f.write(chosen_prompt)

    return chosen_prompt

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

# Define the JSON payload
json_payload = {
    "prompt": generate_shrek_prompt(),
    "negative_prompt": "bad quality, deformed, boring",
    "seed": -1,
    "sampler_name": "DDIM",
    "batch_size": 1,
    "steps": 10,
    "cfg_scale": 7,
    "width": 512,
    "height": 512
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
file_path = "D:\\sentiMation\\assets\\cn_shrek.png"  # Replace 'your_image.png' with the desired file name

# Write the bytes to a file
with open(file_path, "wb") as image_file:
    image_file.write(image_bytes)
