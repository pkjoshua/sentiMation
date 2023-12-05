import os
import datetime
import logging
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def concatenate_videos(video_folder, output_folder):
    video_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith(".mp4")]
    video_files.sort()  # Sort to ensure they are in order

    if not video_files:
        logging.warning("No video files found in the folder.")
        return

    clips = [VideoFileClip(v) for v in video_files]
    final_clip = concatenate_videoclips(clips, method="compose")

    # Generate video file name with current date and time
    current_datetime = datetime.datetime.now()
    output_video_name = current_datetime.strftime("final_output_%m%d%Y%H%M") + ".mp4"
    output_video_path = os.path.join(output_folder, output_video_name)

    final_clip.write_videofile(output_video_path, codec="libx264")

    logging.info(f"Final video created: {output_video_path}")

    # Optional: Close all clips to free memory
    for clip in clips:
        clip.close()

# Specify the directories
generations_folder = 'assets\\upscale_generations'
output_folder = 'output'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Concatenate the videos
concatenate_videos(generations_folder, output_folder)
