import requests
import base64
import json
import logging
import os
import io
from PIL import Image

# Constants
INITIAL_DENOISING_STRENGTH = 0.50
INITIAL_CFG_SCALE = 12
CONTINUING_DENOISING_STRENGTH = 0.45
CONTINUING_CFG_SCALE = 5
INITIAL_WIDTH = 360
SUBSEQUENT_WIDTH = 720
HEIGHT = 640

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to resize image
def resize_image(image_path, width, height):
    with Image.open(image_path) as img:
        resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
        resized_img_path = "temp_resized.jpg"
        resized_img.save(resized_img_path)
        return resized_img_path

# Function to combine two images side by side
def combine_images(left_image_path, right_image_path):
    images = [Image.open(x) for x in [left_image_path, right_image_path]]
    total_width = SUBSEQUENT_WIDTH
    max_height = HEIGHT

    new_im = Image.new('RGB', (total_width, max_height))

    # Left image is the previously generated one, right image is the next input frame
    new_im.paste(Image.open(left_image_path), (0,0))
    new_im.paste(Image.open(right_image_path), (INITIAL_WIDTH,0))

    combined_image_path = "temp_combined.jpg"
    new_im.save(combined_image_path)
    return combined_image_path

# Function to create mask image
def create_mask():
    mask = Image.new("L", (SUBSEQUENT_WIDTH, HEIGHT), 0)
    right_half = Image.new("L", (INITIAL_WIDTH, HEIGHT), 255)
    mask.paste(right_half, (INITIAL_WIDTH, 0))
    mask_path = "mask.jpg"
    mask.save(mask_path)
    return mask_path

# Read prompt from file
def read_prompt(file_path):
    with open(file_path, "r") as file:
        return file.readline().strip()

# Define the API URL
api_url = "http://127.0.0.1:7860/sdapi/v1/img2img"

# Directories
frames_dir = "assets\\frames"
generation_dir = "assets\\lowscale"
reels_dir = "assets\\reels"
os.makedirs(generation_dir, exist_ok=True)
os.makedirs(reels_dir, exist_ok=True)

frame_files = sorted(os.listdir(frames_dir))
previous_generation_path = None
prompt = read_prompt("chosen_prompt.txt")

for index, frame_file in enumerate(frame_files):
    original_frame_path = os.path.join(frames_dir, frame_file)
    resized_frame_path = resize_image(original_frame_path, INITIAL_WIDTH, HEIGHT)

    if index == 0:
        # For the first frame, use the resized frame directly and save the response as is
        init_image = encode_image_to_base64(resized_frame_path)
        denoising_strength = INITIAL_DENOISING_STRENGTH
        cfg_scale = INITIAL_CFG_SCALE
        mask_image = None  # No mask for the first frame
    else:
        # For subsequent frames, combine images and apply mask
        combined_image_path = combine_images(previous_generation_path, resized_frame_path)
        combined_image_base64 = encode_image_to_base64(combined_image_path)

        # Save combined reel image
        reel_path = os.path.join(reels_dir, f"reel_{index:04d}.jpg")
        Image.open(combined_image_path).save(reel_path)
        logging.info(f"Reel {index:04d} saved as {reel_path}.")

        # Create and encode mask
        mask_path = create_mask()
        mask_image = encode_image_to_base64(mask_path)

        init_image = combined_image_base64
        denoising_strength = CONTINUING_DENOISING_STRENGTH
        cfg_scale = CONTINUING_CFG_SCALE


    control_net_args = [{
        "input_image": None,
        "resize_mode": "Just Resize",
        "module": "depth_midas",
        "model": "control_v11f1p_sd15_depth_fp16 [4b72d323]",
        "weight": 0.8,
        "pixel_perfect": True,
        "control_mode": "ControlNet is more important"
    }, {
        "input_image": None,
        "resize_mode": "Just Resize",
        "module": "tile_colorfix+sharp",
        "model": "control_v11f1e_sd15_tile_fp16 [3b860298]",
        "weight": 0.3,
        "pixel_perfect": True,
        "control_mode": "Balanced"
    }, {
        "input_image": None,
        "resize_mode": "Just Resize",
        "module": "none",
        "model": "temporalnetv3 [b146ac48]",
        "weight": 0.2,
        "pixel_perfect": True,
        "control_mode": "ControlNet is more important"
    }]


    # Define the JSON payload
    json_payload = {
        "init_images": [init_image],
        "denoising_strength": denoising_strength,
        "include_init_images": True,
        "mask": None,
        "guidance_scale": 7.5,
        "inpainting_fill": 0,
        "mask_blur": 0,
        "inpaint_full_res": True,
        "inpaint_full_res_padding": 32,
        "prompt": prompt,
        "negative_prompt": "bad quality, deformed, boring, pixelated, blurry, unclear, artifact, nude, nsfw, humans, human hands",
        "batch_size": 1,
        "seed": 1337,
        "sampler_name": "DPM++ 2M Karras",
        "steps": 20,
        "cfg_scale": cfg_scale,
        "width": INITIAL_WIDTH if index == 0 else SUBSEQUENT_WIDTH,
        "height": HEIGHT,
        "alwayson_scripts": {
        "ControlNet": {"args": control_net_args}
        }
    }

  # Call the API
    response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=json_payload)

 # Process the response
    if response.status_code == 200:
        r = response.json()
        if 'images' in r and r['images']:
            image_data = base64.b64decode(r['images'][0])
            with Image.open(io.BytesIO(image_data)) as img:
                if index == 0:
                    # Save the first frame as is
                    first_frame_path = os.path.join(generation_dir, f"generation_{index:04d}.jpg")
                    img.save(first_frame_path)
                    previous_generation_path = first_frame_path
                    logging.info(f"First frame saved as {first_frame_path}.")
                else:
                    # Save the right side of the combined image as the next generation
                    right_side = img.crop((INITIAL_WIDTH, 0, SUBSEQUENT_WIDTH, HEIGHT))
                    next_generation_path = os.path.join(generation_dir, f"generation_{index:04d}.jpg")
                    right_side.save(next_generation_path)

                    previous_generation_path = next_generation_path
                    logging.info(f"Frame {index:04d} saved as {next_generation_path}.")
        else:
            logging.error(f"No image data found in the response for frame: {frame_file}")
    else:
        logging.error(f"API call failed for frame: {frame_file}. Status Code: {response.status_code}, Response: {response.text}")