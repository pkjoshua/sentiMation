import logging
import os
import random
import shutil
from moviepy.editor import *

script_dir = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(filename=os.path.join(script_dir, 'gen.log'), level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def read_prompts_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        prompts = file.readlines()
    return [prompt.strip() for prompt in prompts]

def select_random_video(video_dir):
    videos = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if os.path.isfile(os.path.join(video_dir, f))]
    return random.choice(videos)

def extract_audio_from_video(video_path, output_dir):
    with VideoFileClip(video_path) as video:
        if video.audio:  # Check if the video has an audio track
            audio_output_path = os.path.join(output_dir, 'audio.mp3')
            video.audio.write_audiofile(audio_output_path)
        else:
            logging.warning(f"No audio found in the video: {video_path}")

def move_video_to_used(video_path, used_dir):
    video_name = os.path.basename(video_path)
    used_video_path = os.path.join(used_dir, video_name)

    # Create 'used' directory if it doesn't exist
    if not os.path.exists(used_dir):
        os.makedirs(used_dir, exist_ok=True)

    # If the video already exists in 'used', delete it from 'vids'
    if os.path.exists(used_video_path):
        os.remove(video_path)
        logging.info(f"Deleted existing video from 'vids': {video_path}")
    else:
        shutil.move(video_path, used_dir)
        logging.info(f"Moved video to 'used': {video_path}")

def select_random_prompt(prompt_dir):
    prompt_files = [os.path.join(prompt_dir, f) for f in os.listdir(prompt_dir) if os.path.isfile(os.path.join(prompt_dir, f))]
    chosen_prompt_file = random.choice(prompt_files)
    prompts = read_prompts_from_file(chosen_prompt_file)
    chosen_prompt = random.choice(prompts)
    chosen_prompt_path = os.path.join(script_dir, "chosen_prompt.txt")  # Corrected path construction
    with open(chosen_prompt_path, 'w', encoding='utf-8') as file:
        file.write(chosen_prompt)
    return chosen_prompt

# Adjusted paths
script_dir = os.path.dirname(os.path.abspath(__file__))  # Path to the script's directory
video_dir = os.path.join(script_dir, "assets/vids")
prompt_dir = os.path.join(script_dir, "assets/prompts")
used_dir = os.path.join(script_dir, "assets/used")  # Directory for used videos
audio_dir = os.path.join(script_dir, "assets/audio")

# Ensure the audio directory exists
os.makedirs(audio_dir, exist_ok=True)

# Select and process video
selected_video = select_random_video(video_dir)
selected_video_path = os.path.join(script_dir, "chosen_video.mp4")
shutil.copy(selected_video, selected_video_path)

# Extract and save audio from the video
extract_audio_from_video(selected_video, audio_dir)

# Select and save prompt
select_random_prompt(prompt_dir)

# Move the selected video to the 'used' directory
move_video_to_used(selected_video, used_dir)
