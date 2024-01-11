import cv2
import os
import datetime
import logging
from moviepy.editor import *

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def add_audio_to_video(video_path, audio_path, output_path):
    video_clip = VideoFileClip(video_path)

    if os.path.exists(audio_path):
        audio_clip = AudioFileClip(audio_path)
        if audio_clip.duration >= video_clip.duration:
            final_clip = video_clip.set_audio(audio_clip)
        else:
            logging.warning("Audio file is shorter than the video. Proceeding without audio.")
            final_clip = video_clip
    else:
        logging.info("Audio file does not exist. Creating video without audio.")
        final_clip = video_clip

    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
    final_clip.close()
    logging.info(f"Final video creation complete: {output_path}")

def create_video_from_frames(frame_folder, output_folder, audio_folder, fps):
    images = [img for img in os.listdir(frame_folder) if img.endswith(".jpg")]
    images.sort(key=lambda x: int(x.split('generation_')[1].split('.jpg')[0]))

    if not images:
        logging.warning("No images found in the folder.")
        return
    
    # Determine the width and height from the first image
    frame = cv2.imread(os.path.join(frame_folder, images[0]))
    height, width, layers = frame.shape
    size = (width, height)

    # Generate video file name with current date and time
    current_datetime = datetime.datetime.now()
    output_video_name = current_datetime.strftime("output_%m%d%Y%H%M") + ".mp4"
    output_video_path = os.path.join(output_folder, output_video_name)

    # Initialize video writer
    video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    # Add frames to the video
    for image in images:
        video.write(cv2.imread(os.path.join(frame_folder, image)))

    cv2.destroyAllWindows()
    video.release()

    logging.info(f"Video creation complete: {output_video_path}")

    # Add audio to the video or create video without audio
    audio_path = os.path.join(audio_folder, 'audio.mp3')
    output_video_with_audio = output_video_path.replace('.mp4', '_final.mp4')
    add_audio_to_video(output_video_path, audio_path, output_video_with_audio)

# Specify the directories
frame_folder = 'assets\\upscale'
output_folder = 'output'
audio_folder = 'assets\\audio'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Create the video
create_video_from_frames(frame_folder, output_folder, audio_folder, fps=30)

logging.info("Video creation from upscaled frames is complete.")