import requests
import json
import logging
import base64
import os
import random
import cv2
import shutil  # Import shutil for file operations

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def read_prompts_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        prompts = file.readlines()
    return [prompt.strip() for prompt in prompts]

def select_random_video(video_dir):
    videos = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if os.path.isfile(os.path.join(video_dir, f))]
    return random.choice(videos)

def split_video_into_frames(video_path, frames_dir):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    while success:
        # Save frame with zero-padded filename
        frame_filename = f"frame_{count:04d}.png"
        cv2.imwrite(os.path.join(frames_dir, frame_filename), image)      
        success, image = vidcap.read()
        count += 1

def move_video_to_used(video_path, used_dir):
    if not os.path.exists(used_dir):
        os.makedirs(used_dir, exist_ok=True)
    shutil.move(video_path, used_dir)

def select_random_prompt(prompt_dir):
    prompt_files = [os.path.join(prompt_dir, f) for f in os.listdir(prompt_dir) if os.path.isfile(os.path.join(prompt_dir, f))]
    chosen_prompt_file = random.choice(prompt_files)
    prompts = read_prompts_from_file(chosen_prompt_file)
    with open("chosen_prompt.txt", 'w', encoding='utf-8') as file:
        file.write(random.choice(prompts))

# Directories
video_dir = "assets\\vids"
frames_dir = "assets\\frames"
prompt_dir = "assets\\prompts"
used_dir = "assets\\used"  # Directory for used videos

# Ensure directories exist
os.makedirs(frames_dir, exist_ok=True)

# Select and process video
selected_video = select_random_video(video_dir)
split_video_into_frames(selected_video, frames_dir)

# Move the selected video to the 'used' directory
move_video_to_used(selected_video, used_dir)

# Select and save prompt
select_random_prompt(prompt_dir)
