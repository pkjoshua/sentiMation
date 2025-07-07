import os
import datetime
import logging
from moviepy.editor import *

# Determine the directory of the current script to make paths relative to it
script_dir = os.path.dirname(os.path.realpath(__file__))

# Set up logging with paths relative to the script directory
logging.basicConfig(filename=os.path.join(script_dir, 'gen.log'), level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def add_audio_to_video(frames, size, fps, audio_path, output_path):
    video_clip = ImageSequenceClip(frames, fps=fps).resize(size)

    if os.path.exists(audio_path):
        audio_clip = AudioFileClip(audio_path)
        video_clip = video_clip.set_audio(audio_clip)
    else:
        logging.info("Audio file does not exist. Creating video without audio.")

    video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
    logging.info(f"Final video creation complete: {output_path}")

def create_video_from_frames(frame_folder, output_folder, audio_folder, fps):
    images = [img for img in os.listdir(frame_folder) if img.endswith(".png")]
    # Sort images numerically by extracting the number from the filename
    images.sort(key=lambda x: int(x.split('frame_')[1].split('.')[0]))

    if not images:
        logging.warning("No images found in the folder.")
        return

    # Prepare full paths for each image
    frame_paths = [os.path.join(frame_folder, img) for img in images]

    # Generate video file name with current date and time
    current_datetime = datetime.datetime.now()
    output_video_name = current_datetime.strftime("output_%Y%m%d%H%M%S_final.mp4")
    output_video_path = os.path.join(output_folder, output_video_name)

    # Assume the size from the first image
    first_image = ImageClip(frame_paths[0])
    size = first_image.size

    # Add audio to the video or create video without audio
    audio_path = os.path.join(audio_folder, 'audio.mp3')
    add_audio_to_video(frame_paths, size, fps, audio_path, output_video_path)

# Specify the directories relative to the script's location
frame_folder = os.path.join(script_dir, 'assets', 'upscale')
output_folder = os.path.join(script_dir, 'output')
audio_folder = os.path.join(script_dir, 'assets', 'audio')

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Create the video at 30 fps
create_video_from_frames(frame_folder, output_folder, audio_folder, fps=30)

logging.info("Video creation from upscaled frames is complete.")
