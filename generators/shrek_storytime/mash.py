import cv2
import os
import datetime
import shutil
import logging

# Set up logging
logging.basicConfig(filename="shrek_gen.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def create_video_from_frames(frame_folder, output_folder, fps):
    images = [img for img in os.listdir(frame_folder) if img.endswith(".png")]
    images.sort(key=lambda x: int(x.split('frame')[1].split('.png')[0]))  # Sorting frames

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

def clear_folder(folder):
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f'Failed to delete {file_path}. Reason: {e}')

# Specify the directories
frame_folder = 'upscale'
output_folder = 'output'
lowscale_dir = 'lowscale'
upscale_dir = 'upscale'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Create the video
create_video_from_frames(frame_folder, output_folder, fps=30)

# Clear contents of lowscale and upscale folders
clear_folder(lowscale_dir)
clear_folder(upscale_dir)

logging.info("Cleared contents of lowscale and upscale directories.")
