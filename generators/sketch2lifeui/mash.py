import os
import logging
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Set up logging
logging.basicConfig(filename="gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def mash_videos(video_folder, output_folder):
    video_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith(".mp4")]
    video_files.sort()  # Sort the files if needed

    if not video_files:
        logging.warning("No video files found in the folder.")
        return

    clips = [VideoFileClip(video) for video in video_files]

    # Concatenate all videos
    final_clip = concatenate_videoclips(clips)

    # Generate video file name with current date and time
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
    output_video_path = os.path.join(output_folder, f"final_output_{formatted_datetime}.mp4")

    # Write the final video file
    final_clip.write_videofile(output_video_path, codec="libx264")

    for clip in clips:
        clip.close()

    logging.info(f"Final video creation complete: {output_video_path}")

# Specify the directories
upscale_generations_folder = 'assets/upscale_generations'
output_folder = 'output'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Mash the videos
mash_videos(upscale_generations_folder, output_folder)

logging.info("Mashing of videos completed.")
